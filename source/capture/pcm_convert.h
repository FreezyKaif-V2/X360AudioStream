#ifndef PCM_CONVERT_H
#define PCM_CONVERT_H
#include <stdint.h>
void pcm_stereo_16(const float *planar, uint8_t *out);
typedef struct {
    uint32_t handle, sequence;
    uint16_t rate;
    uint8_t bits, reserved;
    uint32_t length;
    uint8_t pcm[1024];
} PcmSlot;
int pcm_queue_push(PcmSlot *slots, volatile uint32_t *write_index,
                   volatile uint32_t *read_index, uint32_t handle,
                   uint32_t sequence, const float *planar);
#endif
