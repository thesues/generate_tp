#function_declear ='''static int fremovexattr(struct vfs_handle_struct *handle,
#                                       struct files_struct *fsp,
#                                       const char *name)'''
#function_declear= '''
#static ssize_t smb_time_audit_pread_recv(struct tevent_req *req,
#                                         struct vfs_aio_state *vfs_aio_state, int * yy)
#                                         '''

class ParseResult:
    def __init__(self):
        self.return_type = ""
        self.parameters = []
        self.function_name = ""


import jacktokenizer
class Parser:
    def __init__(self, code):
        self.tokenizer = jacktokenizer.JackTokenizer(code)
        self.result = ParseResult()

    def __helper_format_type(self, has_enum, has_const, pointer_num, has_struct, type_name, has_unsigned):
        s = ''
        if has_const:
            s += 'const '
        if has_unsigned:
            s += 'unsigned '
        if has_struct:
            s += 'struct '
        if has_enum:
            s += "enum "
        s += type_name
        if pointer_num > 0 :
            s += ' *' * pointer_num
        return s

    def __parse_arg(self):

        parameter_type = ''
        parameter_name = ''
        pointer_num = 0
        has_struct = False
        has_const = False
        has_enum = False
        has_unsigned = False
        if self.tokenizer.identifier() == 'const':
            #skip const
            has_const = True
            self.tokenizer.advance()
        
        if self.tokenizer.identifier() == 'unsigned':
            has_unsigned = True
            self.tokenizer.advance()
        
        if self.tokenizer.identifier() == 'struct':
            has_struct = True
            self.tokenizer.advance()
        
        if self.tokenizer.identifier() == 'enum':
            has_enum = True
            self.tokenizer.advance()
        
        real_type = self.tokenizer.identifier()
        self.tokenizer.advance()


        while self.tokenizer.identifier() == '*':
            self.tokenizer.advance()
            pointer_num += 1
        

        parameter_type = self.__helper_format_type(has_enum, has_const, pointer_num, has_struct, real_type, has_unsigned)


        parameter_name = self.tokenizer.identifier()
        self.tokenizer.advance()

#        print("type is:  " + parameter_type)
#        print("name is:  " + parameter_name)
        #(type, name)
        self.result.parameters.append((parameter_type, parameter_name))


        if self.tokenizer.identifier() == ',':
            self.tokenizer.advance()
            return True
        else:
            return False

    def run(self):
        self.tokenizer.advance(); # skip static
        self.tokenizer.advance(); # skip static

        is_complex_return = False
        return_type = ''

        #skip const
        if self.tokenizer.identifier() == 'const':
            is_complex_return = True
            self.tokenizer.advance()

        if self.tokenizer.identifier() == 'struct':
            is_complex_return = True
            return_type += 'struct '
            self.tokenizer.advance()


        return_type += self.tokenizer.identifier()
        self.tokenizer.advance()

        while self.tokenizer.identifier() == '*':
            is_complex_return = True
            return_type += ' *'
            self.tokenizer.advance()


        self.result.return_type = return_type
        #function name
        self.result.function_name = self.tokenizer.identifier()


        self.tokenizer.advance() # skip (
        self.tokenizer.advance() # skip (
        
        while self.__parse_arg():
            pass
        return is_complex_return


if __name__ == '__main__':
    code = '''
    static int vfs_lttng_stat(vfs_handle_struct *handle,
                               struct smb_filename *fname)
    '''
    x = Parser(code)
    x.run()
    print x.result.return_type
    print x.result.function_name
    print x.result.parameters
#x = Parser(function_declear)
#x.run()
#print x.result.return_type
#print x.result.function_name
#print x.result.parameters
