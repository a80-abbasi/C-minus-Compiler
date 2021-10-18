from scanner import Scanner

input_file = open('input.txt', 'r')
scanner = Scanner(input_file)
tokens_file = open('token.txt', 'w')
tokens_file.write(str(scanner.line_number))

while True:
    token_type, token_string = scanner.get_next_token()
    print(token_type, token_string)
    if token_type is None:
        break

    if token_string == '\n':
        tokens_file.write(f'\n{scanner.line_number}')

    if token_type != 'WHITESPACE':
        tokens_file.write(f"({token_type}, {token_string}) ")

scanner.close_files()
tokens_file.close()
input_file.close()
