import pickle
import string
f = open('helper/pickle.bin', 'rb')

declare_list = pickle.load(f)


if __name__ == '__main__':
    for i in declare_list:
        if string.find(i, ' stat('):
            print i
#declare_list = ['''
#static ssize_t pwrite(vfs_handle_struct *handle,
#                                     files_struct *fsp,
#                                     const void *data, size_t n,
#                                     off_t offset)
#''',
#'''
#static int get_real_filename(struct vfs_handle_struct *handle,
#                                            const char *path,
#                                            const char *name,
#                                            TALLOC_CTX *mem_ctx,
#                                            char **found_name)
#''',
#'''
#static int get_quota(struct vfs_handle_struct *handle,
#                                        const struct smb_filename *smb_fname,
#                                        enum SMB_QUOTA_TYPE qtype,
#                                        unid_t id,
#                                        SMB_DISK_QUOTA *qt)
#'''
#]
