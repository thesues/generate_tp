import parse


complex_return_tp_c_template = '''
{TP_FUNCTION_DECLARE}
{
        {TP_RETURN_TYPE} result;
        tracepoint(vfs_lttng, {TP_FUNCTION_NAME}_enter {TP_TRACE_CALL_ARGS});
        result = SMB_VFS_NEXT_{TP_UPPER_FUNCTION_NAME}({TP_FUNC_CALL_ARGS});
        tracepoint(vfs_lttng, {TP_FUNCTION_NAME}_exit);
        return result;
}
'''

complex_return_tp_h_template = '''
/* {TP_FUNCTION_NAME} START*/
TRACEPOINT_EVENT(
    vfs_lttng,
    {TP_FUNCTION_NAME}_enter,
    TP_ARGS(
        {TP_ARGS}
    ),
    TP_FIELDS(
        {TP_FIELDS}
    )
)
TRACEPOINT_EVENT(
    vfs_lttng,
    {TP_FUNCTION_NAME}_exit,
    TP_ARGS(
    ),
    TP_FIELDS(
    )
)
/* {TP_FUNCTION_NAME} END*/
'''

void_tp_c_template='''
{TP_FUNCTION_DECLARE}
{
        tracepoint(vfs_lttng, {TP_FUNCTION_NAME}_enter {TP_TRACE_CALL_ARGS});
        SMB_VFS_NEXT_{TP_UPPER_FUNCTION_NAME}({TP_FUNC_CALL_ARGS});
        tracepoint(vfs_lttng, {TP_FUNCTION_NAME}_exit);
}
'''

void_tp_h_template='''
/* {TP_FUNCTION_NAME} START*/
TRACEPOINT_EVENT(
    vfs_lttng,
    {TP_FUNCTION_NAME}_enter,
    TP_ARGS(
        {TP_ARGS}
    ),
    TP_FIELDS(
        {TP_FIELDS}
    )
)
TRACEPOINT_EVENT(
    vfs_lttng,
    {TP_FUNCTION_NAME}_exit,
    TP_ARGS(
    ),
    TP_FIELDS(
    )
)
/* {TP_FUNCTION_NAME} END*/
'''



tp_c_template='''
{TP_FUNCTION_DECLARE}
{
        {TP_RETURN_TYPE} result;
        tracepoint(vfs_lttng, {TP_FUNCTION_NAME}_enter {TP_TRACE_CALL_ARGS});
        result = SMB_VFS_NEXT_{TP_UPPER_FUNCTION_NAME}({TP_FUNC_CALL_ARGS});
        tracepoint(vfs_lttng, {TP_FUNCTION_NAME}_exit, result);
        return result;
}
'''
tp_h_template='''
/* {TP_FUNCTION_NAME} START*/
TRACEPOINT_EVENT(
    vfs_lttng,
    {TP_FUNCTION_NAME}_enter,
    TP_ARGS(
        {TP_ARGS}
    ),
    TP_FIELDS(
        {TP_FIELDS}
    )
)
TRACEPOINT_EVENT(
    vfs_lttng,
    {TP_FUNCTION_NAME}_exit,
    TP_ARGS(
        {TP_RETURN_TYPE}, result
    ),
    TP_FIELDS(
        ctf_integer({TP_FIELD_RETURN_TYPE}, retval, {TP_FIELD_RETURN_VALUE})
    )
)
/* {TP_FUNCTION_NAME} END*/
'''

def output_tp_c_h(pcode):
    x = parse.Parser(pcode.strip())
    #if the return is complex, do not tracepoint the return value
    is_complex_return = x.run()

    #print x.result.function_name
    #print x.result.parameters
    #print x.result.return_type
    #change function name
    TP_FUNCTION_NAME = 'vfs_lttng_' + x.result.function_name
    #change return type
    #TP_RETURN_TYPE = 'int' if x.result.return_type == 'NTSTATUS' else x.result.return_type
    TP_RETURN_TYPE = x.result.return_type

    requires={'fsp':'ctf_string(filename, fsp->fsp_name->base_name)', 
              'smb_fname':'ctf_string(filename, smb_fname->base_name)',
              'fname'    :'ctf_string(filename, fname->base_name)',
              'offset'   :'ctf_integer(off_t, offset, offset)',
              'tofd'     :'ctf_integer(int, tofd, tofd)',
              'fromid'   :'ctf_integer(int, fromfd, fromfd)',
              'name'     :'ctf_string(name, name)', 
              'n'        :'ctf_integer(size_t, n, n)',
              'flags'    :'ctf_integer(int, flags, flags)',
              'mode'     :'ctf_integer(mode_t, mode, mode)'
              }

    #only one of these is nessary
    #filter parameters
    filtered_parameters = []
    uniq_set = set(('smb_fname', 'fname', 'fsp'))
    uniq_bool = False
    for i in x.result.parameters:
        if i[1] in uniq_set and uniq_bool == True:
            continue
        elif i[1] in uniq_set:
            uniq_bool = True
            filtered_parameters.append(i)
        else:
            filtered_parameters.append(i)

    TP_ARGS=''
    TP_FIELDS=''

    for i in filtered_parameters:
        if i[1] in requires:
            if TP_ARGS != '':
                TP_ARGS += ',\n' + 2 * 4 * ' '
            TP_ARGS += "%s, %s" % (i[0], i[1])
    
    #print TP_ARGS


    for i in filtered_parameters:
        if i[1] in requires:
            if TP_FIELDS != '':
                TP_FIELDS +='\n' + 2 * 4 * ' ' #FUCK, TP_FIELD has no comma
            TP_FIELDS += requires[i[1]]
    #print TP_FIELDS

    TP_TRACE_CALL_ARGS = ''
    TP_FUNC_CALL_ARGS = ''


    for i in filtered_parameters:
        if i[1] in requires:
            TP_TRACE_CALL_ARGS += ', '
            TP_TRACE_CALL_ARGS += i[1]

    for i in x.result.parameters:
        if TP_FUNC_CALL_ARGS != '':
            TP_FUNC_CALL_ARGS += ', '
        TP_FUNC_CALL_ARGS += i[1]

    #import pdb
    #if x.result.function_name == 'stat':
    #    pdb.set_trace()
    ##fuck, make sure only function name is replaced
    TP_FUNCTION_DECLARE = pcode.replace(x.result.function_name+'(', TP_FUNCTION_NAME+'(')

    TP_UPPER_FUNCTION_NAME = x.result.function_name.upper()

    def replace_lttng_h(is_complex_return):

        local_return_type = x.result.return_type
        local_return_value = "result"
        template = tp_h_template
        if is_complex_return:
            template = complex_return_tp_h_template
        elif local_return_type == "void":
            template = void_tp_h_template
        elif local_return_type == "NTSTATUS":
            #change return type
            local_return_value = "result.v"
            local_return_type  = "int"

        return template.replace('{TP_RETURN_TYPE}', TP_RETURN_TYPE).\
        replace('{TP_FUNCTION_NAME}', TP_FUNCTION_NAME).\
        replace('{TP_ARGS}', TP_ARGS).\
        replace('{TP_FIELDS}', TP_FIELDS).\
        replace('{TP_FIELD_RETURN_VALUE}', local_return_value).\
        replace('{TP_FIELD_RETURN_TYPE}', local_return_type)

    def replace_lttng_c(is_complex_return):
        
        template = tp_c_template
        if is_complex_return:
            template = complex_return_tp_c_template
        elif TP_RETURN_TYPE == "void":
            template = void_tp_c_template

        return template.replace('{TP_FUNCTION_DECLARE}', TP_FUNCTION_DECLARE)\
        .replace('{TP_UPPER_FUNCTION_NAME}', TP_UPPER_FUNCTION_NAME)\
        .replace('{TP_FUNCTION_NAME}', TP_FUNCTION_NAME)\
        .replace('{TP_TRACE_CALL_ARGS}', TP_TRACE_CALL_ARGS)\
        .replace('{TP_FUNC_CALL_ARGS}', TP_FUNC_CALL_ARGS)\
        .replace('{TP_RETURN_TYPE}', TP_RETURN_TYPE)

    lttng_h = replace_lttng_h(is_complex_return)
    lttng_c = replace_lttng_c(is_complex_return)
    #print lttng_c
    #print lttng_h
    return (TP_FUNCTION_NAME, lttng_c, lttng_h)


if __name__ == '__main__':
    pcode = '''
static int vfs_lttng_open(vfs_handle_struct *handle,
			       struct smb_filename *fname,
			       files_struct *fsp,
			       int flags, mode_t mode)
    '''
    fn_name, c, h = output_tp_c_h(pcode)
    print c
    print h