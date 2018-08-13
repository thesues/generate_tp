import string
import pickle
f = open('p.txt', 'r')
time_audit_file= open('/root/rpmbuild/BUILD/samba-4.7.1/source3/modules/vfs_time_audit.c')

time_audit_content = time_audit_file.read();

final_list = []

for line in f:
	#search the whole function name
	function_start = string.find(time_audit_content, line.strip() + '(')
	function_end = string.find(time_audit_content, '{', function_start)
	line_start = string.rfind(time_audit_content, '\n', 0, function_start)
	
	x = time_audit_content[line_start:function_end].replace('smb_time_audit_','')
	print x
	final_list.append(x)
	

f.close()
time_audit_file.close()


f = open('pickle.bin', 'wb')
pickle.dump(final_list, f)
f.close()


