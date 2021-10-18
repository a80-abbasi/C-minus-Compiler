# Maziar Shamsipour 98101844
# Ali Abbasi 98105879


from scanner import Scanner

input_file = open('input.txt', 'r')
scanner = Scanner(input_file)
tokens_file = open('token.txt', 'w')
newline = False
print_line_number = True

while True:
    token_type, token_string = scanner.get_next_token()
    # print(token_type, token_string)
    if token_type is None:
        break

    if token_string == '\n':
        newline = True
        print_line_number = True
        # tokens_file.write('\n')

    if token_type != 'WHITESPACE' and token_type != 'COMMENT':
        if newline:
            tokens_file.write(f'\n')
            newline = False
        if print_line_number:
            tokens_file.write(f'{scanner.line_number}.\t')
            print_line_number = False
        tokens_file.write(f"({token_type}, {token_string}) ")

scanner.close_files()
tokens_file.close()
input_file.close()
