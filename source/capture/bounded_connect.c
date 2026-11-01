#include <stdint.h>
typedef int32_t (*ModuleFn)(const char *, void **);
typedef int32_t (*ProcFn)(void *, uint32_t, void **);
typedef int32_t (*IoctlFn)(uint32_t, uint32_t, uint32_t, uint32_t *);
typedef int32_t (*ConnectFn)(uint32_t, const void *, uint32_t);
typedef struct { uint32_t count; uint32_t socket; } OneSocket;
typedef struct { int32_t seconds, microseconds; } Timeval;
typedef int32_t (*SelectFn)(uint32_t, uint32_t, void *, OneSocket *, OneSocket *, Timeval *);

__attribute__((section(".connect_helper"), noinline))
int32_t bounded_connect(uint32_t socket, const void *address, uint32_t length) {
    ModuleFn module=(ModuleFn)0x91d1d484u;
    ProcFn procedure=(ProcFn)0x91d1d474u;
    IoctlFn ioctl_socket=(IoctlFn)0x91d1d3e4u;
    ConnectFn connect_socket=(ConnectFn)0x91d0fa18u;
    void *xam=0, *select_address=0;
    if (module("xam.xex", &xam)<0 || !xam ||
        procedure(xam, 15, &select_address)<0 || !select_address) return -1;
    uint32_t mode=1;
    if (ioctl_socket(1, socket, 0x8004667eu, &mode)!=0) return -1;
    int32_t result=connect_socket(socket,address,length);
    if (result!=0) {
        OneSocket writable={1,socket}, failed={1,socket};
        Timeval timeout={2,0};
        int32_t selected=((SelectFn)select_address)(1,0,0,&writable,&failed,&timeout);
        if (selected<=0 || writable.count!=1 || failed.count!=0) result=-1;
        else result=0;
    }
    mode=0;
    if (ioctl_socket(1, socket, 0x8004667eu, &mode)!=0) return -1;
    return result;
}
