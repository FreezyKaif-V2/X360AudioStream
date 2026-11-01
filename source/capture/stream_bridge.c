/* Experimental bridge. The callback never performs PCM conversion or I/O. */
#include "mec_handoff.h"
#ifdef MEC_OWN_CONVERTER
#include "pcm_convert.h"
#endif
#include <stdint.h>

typedef int32_t (*ModuleFn)(const char *, void **);
typedef int32_t (*ProcFn)(void *, uint32_t, void **);
typedef int32_t (*ThreadFn)(void **, uint32_t, uint32_t *, void *, void *, void *, uint32_t);
typedef void (*TerminateFn)(uint32_t);
typedef void *(*AllocateFn)(uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);
typedef void (*ConvertFn)(void *, const float *);

#define MODULE ((ModuleFn)0x91d1d484u)
#define PROC ((ProcFn)0x91d1d474u)
#define THREAD ((ThreadFn)0x91d1d7b4u)
#define TERMINATE ((TerminateFn)0x91d1d6d4u)
#define ALLOCATE ((AllocateFn)0x91d1d544u)
#define CONVERT ((ConvertFn)0x91d09560u)

#ifdef MEC_BOOT_DELAY
/* Experimental: allow the dashboard and networking to finish booting before
   entering the original connection path. Never run on the loader thread. */
void bridge_boot_wait(void) {
    ((void (*)(uint32_t))0x91d18f68u)(15000);
}
#endif

/* This small state is in disabled video workspace, not the audio queue.
   The substantially larger handoff uses separately allocated memory. */
typedef struct {
    volatile uint32_t state, status, callbacks, pumped;
    MecClient client;
    void *handle;
    MecCapture capture;
    MecHandoff *queue;
    volatile uint32_t stale_discarded;
    volatile int32_t timeout_result;
} Bridge;
static Bridge bridge;

#ifdef MEC_ASYNC_PUMP
void bridge_pump(void);
static void thread_start(uint32_t (*start)(void *), void *context);
__attribute__((section(".pump_worker"), noinline))
static uint32_t pump_worker(void *unused) {
    (void)unused;
    for (;;) {
        bridge_pump();
        ((void (*)(uint32_t))0x91d18f68u)(2);
    }
    return 0;
}
#endif

#ifdef MEC_OWN_CONVERTER
__attribute__((section(".pcm_wrapper"), noinline))
static void convert_frame(void *handle, const float *frame) {
    volatile uint32_t *write_index=(volatile uint32_t *)0x91d44498u;
    volatile uint32_t *read_index=(volatile uint32_t *)0x91d4449cu;
    volatile uint32_t *sequence=(volatile uint32_t *)0x91d444acu;
    uint32_t next=*sequence+1;
    if (pcm_queue_push((PcmSlot *)0x91d34060u, write_index, read_index,
                       (uint32_t)(uintptr_t)handle, next, frame))
        *sequence=next;
}
#endif

#ifdef MEC_SEND_TIMEOUT
/* Preserve the existing insecure-socket option and bound blocked sends. */
__attribute__((section(".sock_setup"), noinline))
int32_t bridge_socket_setup(uint32_t socket, uint32_t level, uint32_t option,
                            const void *value, uint32_t length) {
    typedef int32_t (*SetOptFn)(uint32_t, uint32_t, uint32_t, const void *, uint32_t);
    SetOptFn setopt = (SetOptFn)0x91d0f9f8u;
    int32_t result = setopt(socket, level, option, value, length);
    uint32_t timeout_ms = 250;
    bridge.timeout_result = setopt(socket, 0xffff, 0x1005, &timeout_ms, sizeof(timeout_ms));
    return result;
}
#endif

static void callback(void *unused) {
    (void)unused;
    __atomic_fetch_add(&bridge.callbacks, 1, __ATOMIC_RELAXED);
    void *handle = __atomic_load_n(&bridge.handle, __ATOMIC_ACQUIRE);
    if (handle) mec_handoff_capture(bridge.queue, bridge.capture, handle);
}

static uint32_t worker(void *unused) {
    (void)unused;
    void *kernel = 0, *reg = 0, *capture = 0, *handle = 0;
    MecHandoff *q = ALLOCATE(0, sizeof(*q), 4, 0, UINT32_MAX, 0);
    if (!q) { bridge.status = 0x101; return 1; }
    /* Sample slots do not need initialization before the first capture. */
    q->write_index = q->read_index = q->busy = q->dropped = q->errors = 0;
    bridge.queue = q;
    if (MODULE("xboxkrnl.exe", &kernel) < 0 || !kernel) { bridge.status = 0x102; return 1; }
    if (PROC(kernel, 800, &reg) < 0 || !reg) { bridge.status = 0x103; return 1; }
    if (PROC(kernel, 802, &capture) < 0 || !capture) { bridge.status = 0x104; return 1; }
    bridge.capture = (MecCapture)capture;
    bridge.client.callback = callback;
    bridge.client.context = &bridge;
    if (((MecRegister)reg)(&bridge.client, &handle) < 0 || !handle) {
        bridge.status = 0x105; return 1;
    }
    __atomic_store_n(&bridge.handle, handle, __ATOMIC_RELEASE);
#ifdef MEC_ASYNC_PUMP
    void *pump_thread = 0;
    uint32_t pump_id = 0;
    /* Keep capture conversion on hardware thread 3; the sender currently
       starts on hardware thread 2. The top byte carries the affinity mask. */
    if (THREAD(&pump_thread, 0x10000, &pump_id, (void *)thread_start,
               (void *)pump_worker, 0, 0x08000002u) < 0) {
        bridge.status = 0x107; return 1;
    }
#endif
    bridge.status = 2;
    return 0;
}

static void thread_start(uint32_t (*start)(void *), void *context) {
    TERMINATE(start(context));
}

/* Called in the existing stream worker after initial queue setup. */
void bridge_start(void) {
    if (bridge.state) return;
    bridge.state = 1;
    bridge.status = 1;
    void *thread = 0;
    uint32_t id = 0;
    if (THREAD(&thread, 0x10000, &id, (void *)thread_start, (void *)worker, 0, 2) < 0)
        bridge.status = 0x106;
}

/* The socket worker owns the read side and existing PCM converter. */
void bridge_pump(void) {
    MecHandoff *q = bridge.queue;
    if (!q || !__atomic_load_n(&bridge.handle, __ATOMIC_ACQUIRE)) return;
    /* If the consumer fell completely behind, discard stale frames on the
       consumer side only. The producer never changes the read index. */
#ifndef MEC_ASYNC_PUMP
    uint32_t read = __atomic_load_n(&q->read_index, __ATOMIC_RELAXED);
    uint32_t write = __atomic_load_n(&q->write_index, __ATOMIC_ACQUIRE);
    if (write - read >= MEC_HANDOFF_SLOTS) {
        uint32_t discard = write - read - 2;
        __atomic_store_n(&q->read_index, read + discard, __ATOMIC_RELEASE);
        bridge.stale_discarded += discard;
    }
#endif
    /* A 2 ms sleep can wake much later on the console. Drain the bounded
       queue rather than consuming only one 5.33 ms frame per wakeup. */
    for (unsigned i = 0; i < MEC_HANDOFF_SLOTS; ++i) {
        const float *frame = mec_handoff_peek(q);
        if (!frame) break;
        /* Avoid filling the network with digital silence. Test every sample,
           retaining even very quiet sounds rather than using a threshold. */
#ifdef MEC_ASYNC_PUMP
#ifdef MEC_OWN_CONVERTER
        convert_frame(bridge.handle, frame);
#else
        CONVERT(bridge.handle, frame);
#endif
#else
        const uint32_t *bits = (const uint32_t *)(const void *)frame;
        unsigned i_sample = 0;
        while (i_sample < MEC_CHANNELS * MEC_FRAMES &&
               (bits[i_sample] & 0x7fffffffu) == 0) ++i_sample;
        if (i_sample != MEC_CHANNELS * MEC_FRAMES)
            CONVERT(bridge.handle, frame);
#endif
        mec_handoff_release(q);
        ++bridge.pumped;
    }
}
