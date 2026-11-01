#ifndef MEC_PROBE_H
#define MEC_PROBE_H

#include <stdint.h>

enum { MEC_CHANNELS = 6, MEC_FRAMES = 256 };
typedef struct { void (*callback)(void *); void *context; } MecClient;
typedef int32_t (*MecRegister)(MecClient *, void **);
typedef int32_t (*MecCapture)(void *, float *);
typedef int32_t (*MecUnregister)(void *);

typedef struct {
    MecClient client;
    void *handle;
    MecCapture capture;
    volatile uint32_t callbacks;
    volatile uint32_t captured;
    volatile uint32_t nonzero_frames;
    volatile uint32_t errors;
    volatile uint32_t busy;
    volatile uint32_t dropped;
    volatile uint32_t stopping;
    float samples[MEC_CHANNELS * MEC_FRAMES] __attribute__((aligned(128)));
} MecProbe;

/* Caller must initialize probe to zero. Registration belongs on a worker,
   outside loader lock. This is a diagnostic core, not a loadable XEX. */
int mec_probe_start(MecProbe *probe, MecRegister register_client, MecCapture capture);
void mec_probe_callback(void *context);
/* A successful return alone does not prove the kernel drained all callbacks. */
int mec_probe_request_stop(MecProbe *probe, MecUnregister unregister_client);

#endif
