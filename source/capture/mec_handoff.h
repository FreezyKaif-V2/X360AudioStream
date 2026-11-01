#ifndef MEC_HANDOFF_H
#define MEC_HANDOFF_H

#include "mec_probe.h"

/* One audio callback producer and one streaming-thread consumer. A claimed
   frame remains owned by the consumer until mec_handoff_release(). */
/* ~85 ms of headroom for console scheduling and socket jitter. */
enum { MEC_HANDOFF_SLOTS = 16 };
typedef struct {
    volatile uint32_t write_index, read_index, busy, dropped, errors;
    float frames[MEC_HANDOFF_SLOTS][MEC_CHANNELS * MEC_FRAMES]
        __attribute__((aligned(128)));
} MecHandoff;

void mec_handoff_capture(MecHandoff *q, MecCapture capture, void *handle);
const float *mec_handoff_peek(MecHandoff *q);
void mec_handoff_release(MecHandoff *q);
#endif
