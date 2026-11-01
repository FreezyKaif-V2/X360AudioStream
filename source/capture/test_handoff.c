#include "mec_handoff.h"
#include <assert.h>
#include <stdint.h>
#include <string.h>

static int32_t fake_capture(void *handle, float *samples) {
    samples[0] = (float)(uintptr_t)handle;
    return 0;
}
static int32_t failed_capture(void *handle, float *samples) {
    (void)handle; (void)samples; return -1;
}
int main(void) {
    static MecHandoff q;
    assert(!mec_handoff_peek(&q));
    for (uintptr_t i = 1; i <= MEC_HANDOFF_SLOTS; ++i)
        mec_handoff_capture(&q, fake_capture, (void *)i);
    mec_handoff_capture(&q, fake_capture, (void *)(MEC_HANDOFF_SLOTS + 1));
    assert(q.dropped == 1);
    for (unsigned i = 1; i <= MEC_HANDOFF_SLOTS; ++i) {
        assert(mec_handoff_peek(&q)[0] == (float)i);
        mec_handoff_release(&q);
    }
    assert(!mec_handoff_peek(&q));
    mec_handoff_capture(&q, failed_capture, (void *)1);
    assert(q.errors == 1 && !mec_handoff_peek(&q));
    q.write_index = q.read_index = UINT32_MAX;
    mec_handoff_capture(&q, fake_capture, (void *)7);
    assert(mec_handoff_peek(&q)[0] == 7);
    mec_handoff_release(&q);
    assert(!mec_handoff_peek(&q));
    q.busy = 1;
    mec_handoff_capture(&q, fake_capture, (void *)1);
    assert(q.dropped == 2);
    return 0;
}
