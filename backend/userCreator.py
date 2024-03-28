options = "'A )  A  single  valueB )  An  empty  listC )  A  sequence  of  numbersD )  An  error'"

# Split the options into a list of lines
lines = options.splitlines()

# Print each option on a separate line
for line in lines:
    print(line.strip())  # Remove any leading/trailing whitespace