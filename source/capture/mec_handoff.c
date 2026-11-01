#include "mec_handoff.h"

void mec_handoff_capture(MecHandoff *q, MecCapture capture, void *handle) {
    if (!q || !capture || !handle) return;
    if (__atomic_exchange_n(&q->busy, 1, __ATOMIC_ACQUIRE)) {
        __atomic_fetch_add(&q->dropped, 1, __ATOMIC_RELAXED);
        return;
    }
    uint32_t w = __atomic_load_n(&q->write_index, __ATOMIC_RELAXED);
    uint32_t r = __atomic_load_n(&q->read_index, __ATOMIC_ACQUIRE);
    if (w - r >= MEC_HANDOFF_SLOTS) {
        __atomic_fetch_add(&q->dropped, 1, __ATOMIC_RELAXED);
    } else if (capture(handle, q->frames[w % MEC_HANDOFF_SLOTS]) < 0) {
        __atomic_fetch_add(&q->errors, 1, __ATOMIC_RELAXED);
    } else {
        __atomic_store_n(&q->write_index, w + 1, __ATOMIC_RELEASE);
    }
    __atomic_store_n(&q->busy, 0, __ATOMIC_RELEASE);
}

const float *mec_handoff_peek(MecHandoff *q) {
    uint32_t r = __atomic_load_n(&q->read_index, __ATOMIC_RELAXED);
    if (r == __atomic_load_n(&q->write_index, __ATOMIC_ACQUIRE)) return 0;
    return q->frames[r % MEC_HANDOFF_SLOTS];
}

void mec_handoff_release(MecHandoff *q) {
    uint32_t r = __atomic_load_n(&q->read_index, __ATOMIC_RELAXED);
    __atomic_store_n(&q->read_index, r + 1, __ATOMIC_RELEASE);
}
