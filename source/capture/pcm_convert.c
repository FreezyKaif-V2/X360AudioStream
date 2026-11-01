#include "pcm_convert.h"

/* Convert IEEE-754 float bits to signed PCM without using the FPU. */
static int32_t sample(uint32_t bits) {
    uint32_t exponent=(bits>>23)&255u;
    uint32_t sign=bits>>31;
    if (exponent==255u) return 0;
    if (exponent>=127u) return sign ? -32768 : 32767;
    if (exponent<112u) return 0;
    uint32_t magnitude=((bits&0x7fffffu)|0x800000u)>>(135u-exponent);
    return sign ? -(int32_t)magnitude : (int32_t)magnitude;
}

void pcm_stereo_16(const float *planar, uint8_t *out) {
    for (unsigned i=0; i<256; ++i) {
        union { float f; uint32_t u; } left_bits, right_bits;
        left_bits.f=planar[i]; right_bits.f=planar[i+256];
        uint16_t left=(uint16_t)sample(left_bits.u);
        uint16_t right=(uint16_t)sample(right_bits.u);
        out[4*i]=(uint8_t)left; out[4*i+1]=(uint8_t)(left>>8);
        out[4*i+2]=(uint8_t)right; out[4*i+3]=(uint8_t)(right>>8);
    }
}

int pcm_queue_push(PcmSlot *slots, volatile uint32_t *write_index,
                   volatile uint32_t *read_index, uint32_t handle,
                   uint32_t sequence, const float *planar) {
    uint32_t w=__atomic_load_n(write_index,__ATOMIC_RELAXED);
    uint32_t r=__atomic_load_n(read_index,__ATOMIC_ACQUIRE);
    if (w-r>=64) return 0;
    PcmSlot *slot=&slots[w%64];
    slot->handle=handle; slot->sequence=sequence; slot->rate=48000;
    slot->bits=16; slot->reserved=0; slot->length=1024;
    pcm_stereo_16(planar,slot->pcm);
    __atomic_store_n(write_index,w+1,__ATOMIC_RELEASE);
    return 1;
}
