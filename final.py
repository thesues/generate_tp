import generate
import re
from test import declare_list

def update_function_name_to_smb(name):
    return re.match('vfs_lttng_(\w+)', name).group(1) + "_fn"

def build_vfs_list(function_list):
    vfs_fns='\nstatic struct vfs_fn_pointers vfs_lttng_fns = {\n'
    first = True
    for i in function_list:
        if first == True:
            vfs_fns += 8 * ' ' + ".%s = %s" % (i[0], i[1])
            first = False
            continue
        vfs_fns += ",\n        .%s = %s" % (i[0], i[1])

    vfs_fns += '\n};\n'

    return vfs_fns


def create_final_c(c_code, vfs_functions):
    f = open('final/vfs_lttng.c', "w")
    c_txt = '''
#define TRACEPOINT_CREATE_PROBES
/*
* The header containing our TRACEPOINT_EVENTs.
*/
#define TRACEPOINT_DEFINE


#include "includes.h"
#include "smbd/smbd.h"
#include "ntioctl.h"
#include "lib/util/tevent_unix.h"
#include "lib/util/tevent_ntstatus.h"

#include "vfs_lttng_tp.h"

    '''
    c_txt += c_code

    #vfs_list
    c_txt += vfs_functions

    c_txt += '''
NTSTATUS vfs_lttng_init(TALLOC_CTX *);
NTSTATUS vfs_lttng_init(TALLOC_CTX *ctx)
{
    return smb_register_vfs(SMB_VFS_INTERFACE_VERSION, "lttng",
                            &vfs_lttng_fns);
}
    '''
    f.write(c_txt)
    f.close()


def create_final_h(h_code):
    f = open('final/vfs_lttng_tp.h', 'w')
    h_txt = '''
#undef TRACEPOINT_PROVIDER
#define TRACEPOINT_PROVIDER vfs_lttng

#undef TRACEPOINT_INCLUDE
#define TRACEPOINT_INCLUDE "modules/vfs_lttng_tp.h"

#if !defined(VFS_LTTNG_TP_H) || defined(TRACEPOINT_HEADER_MULTI_READ)
#define VFS_LTTNG_TP_H

#include <lttng/tracepoint.h>
#include <includes.h> 
    '''
    h_txt += h_code
    h_txt += '''
#endif /* VFS_LTTNG_TP_H */
#include <lttng/tracepoint-event.h>
    '''
    f.write(h_txt)
    f.close()


if __name__ == '__main__':
    function_list=[]
    c_text = ''
    h_text = ''    
    for code in declare_list:
        f_name, c_code, h_code = generate.output_tp_c_h(code)

        if 'pread_send' in f_name or 'pread_recv' in f_name or \
        'pwrite_send' in f_name or 'pwrite_recv' in f_name or \
        'fsync_send' in f_name or 'fsync_recv' in f_name or \
        'rewinddir' in f_name:
            print "ignore: " + f_name
            continue
        c_text += c_code
        h_text += h_code

        function_list.append((update_function_name_to_smb(f_name), f_name))
        
    create_final_c(c_text, build_vfs_list(function_list))
    create_final_h(h_text)
