# How to 

```
python final.py

```

It reads function declares, and generate lttng template code

# 1. Modify after generating the code

```
vfs_lttng_durable_reconnect_enter

Change to

TRACEPOINT_EVENT(
    vfs_lttng,
    vfs_lttng_durable_reconnect_enter,
    TP_ARGS(
        struct files_struct * *, fsp
    ),
    TP_FIELDS(
        ctf_string(filename, (*fsp)->fsp_name->base_name)
    )
)

Because fsp is a (struct files_struct**)

```



# 2. Modify after generating the code

```
In vfs_lttng_get_alloc_size_exit, remove fsp, 
fsp may be empty

```
