#include "pcm_convert.h"
#include <assert.h>
#include <math.h>

int main(void) {
    float planar[6*256]={0};
    uint8_t output[1024];
    planar[0]=0.5f; planar[256]=-0.5f;
    planar[1]=2.0f; planar[257]=-2.0f;
    planar[2]=NAN; planar[258]=0.0f;
    pcm_stereo_16(planar,output);
    assert(output[0]==0 && output[1]==0x40 && output[2]==0 && output[3]==0xc0);
    assert(output[4]==0xff && output[5]==0x7f && output[6]==0 && output[7]==0x80);
    assert(output[8]==0 && output[9]==0 && output[10]==0 && output[11]==0);
    static PcmSlot slots[64];
    volatile uint32_t w=0,r=0;
    assert(sizeof(PcmSlot)==0x410);
    assert(pcm_queue_push(slots,&w,&r,9,3,planar));
    assert(w==1 && slots[0].handle==9 && slots[0].sequence==3);
    assert(slots[0].rate==48000 && slots[0].bits==16 && slots[0].length==1024);
    assert(slots[0].pcm[1]==0x40 && slots[0].pcm[3]==0xc0);
    w=64; r=0;
    assert(!pcm_queue_push(slots,&w,&r,9,3,planar) && w==64);
    w=r=UINT32_MAX;
    assert(pcm_queue_push(slots,&w,&r,9,3,planar) && w==0);
    uint32_t state=0x12345678u;
    for (unsigned n=0;n<10000;++n) {
        union { uint32_t u; float f; } value;
        state=state*1664525u+1013904223u; value.u=state;
        planar[0]=value.f; pcm_stereo_16(planar,output);
        int expected;
        if (!isfinite(value.f)) expected=0;
        else if (value.f>=1.0f) expected=32767;
        else if (value.f<=-1.0f) expected=-32768;
        else expected=(int)(value.f*32768.0f);
        uint16_t actual=(uint16_t)(output[0]|((uint16_t)output[1]<<8));
        assert(actual==(uint16_t)expected);
    }
    return 0;
}
