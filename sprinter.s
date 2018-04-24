# Sprinter.
# Kopierer inneholdet i en variabel til en annen variabel
# gitt formatet.

# C Function: int sprinter(uchar* res, uchar* format ...)

# Registre:
# ECX - Byte counter
# EBX - Result pointer
# EDX - Format pointer

# EAX - WORK
# ESI - WORK
# EDI - WORK
.globl sprinter

sprinter:
	pushl	%ebp					# Start
	movl	%esp, %ebp 		# Start

	# pushl %esi 					# Store value of %ESI
	# pushl %edi					# Store value of %EDI

	movl $0, %ecx				# % Use %ecx for counter

	movl 8(%ebp), %ebx 	# Move pointer-Res to %EBX
	movl 12(%ebp), %edx # Move pointer-Format to %EDX
	addl $16, %ebp 			# make %EBP point to first variable argument



	# Master loop:
	# Check FORMAT if % is found or '0' (endbyte) is found.
	# Jump to corresponding function.
	# When done, increase counters & pointers and do loop again.
	loop_master:
		movb (%edx), %al   	# Store first char of format in %al

		cmpb $37, %al     # Compare with ASCII '%'
		je format_detector # If match, jump to format_detector

		cmpb $0, %al      # Compare with '\0'
		je done						# If yes jump

		movb %al, (%ebx)    # if none, move char to %al

		jmp increment			# Increase counters & pointers


	# '%' Found! Point to next char in format,
	# and find out if its 's', 'd', 'c', 'u' , 'x' , '#'  or ' %'
	format_detector:
		incl %edx            # Point to char after '%' in format.
		movb (%edx), %al     # Move this char into %AL.

		cmpb $115,  %al     # Compare format with 's'
		je string						# Jump to function which handles 's'

		cmpb $100,  %al     # Compare 'd'...
		je integer

		cmpb $99,  %al     # Compare 'c'...
		je character

		cmpb $117,  %al    # Compare 'u'...
		je unsigned

		cmpb $120,  %al    # Compare 'x'...
		je hex

		cmpb $35,  %al    # Compare '#'...
		je zhex

		cmpb $37,  %al    # Compare '%'...
		je percent


	percent:
		movb $37, (%ebx)  # move ASCII value for '%' to result

		jmp increment     # Done, increase counters.



	character:
			movb (%ebp), %al   # Move current char to %AL
			movb %al, (%ebx) 	 # Copy to result

			addl $4, %ebp      # Make %EBP point to next arg.

			jmp increment      # Increase and return to main loop.

	string:
		movl (%ebp), %esi  # Move argument address to %ESI
		movb (%esi), %al   # Move first char to %AL

		cmpb $0, %al       # If '\0' byte, copying is done. exit.
		je string_done

		movb %al, (%ebx)	 # If not '\0' byte, copy char to result.

		incl (%ebp)        # Increase string pointer, result pointer and counter.
		incl %ebx
		incl %ecx

		jmp string  			 # Start again with next char.


	string_done:
		addl $4, %ebp      # Increase pointer to next arg

		incl %edx					 # Increase pointer to format

		jmp loop_master



	unsigned:
		pushl %edx
		movl $0, %esi     		 # Turned my work register  %ESI into a digit counter
		movl (%ebp), %eax 		 # move integer to work register %EAX
		jmp positive_integer

	integer:
		pushl %edx        		 # Push format to stack
		movl $0, %esi     		 # Turned my work register into a digit counter

		movl (%ebp), %eax 		 # move integer to work register %EAX

		cmp $0, %eax      	 	# check if it's a negative number
		jns positive_integer  # It isn't.

		# or is it? (hmmmmmmm)
		movb $45, (%ebx)      # Since it's a negative number add '-' to result.
		negl %eax 						# Make work register arithmeticly negative.

		incl %ecx             # Increase counter
		incl %ebx             # Increase Result pointer.



	positive_integer:
		movl $10, %edi        # Use %ESI for division by 10
		movl $0, %edx					# Reset %EDX. We need this register for division
		divl %edi    					# Divide %EAX by %ESI (10) function divl stores remainder in EDX

		addl $48, %edx        # add ASCII '0' to remainder of division.
		push %edx							# Push the digit to stack. Where they will be stored in LITTLE endian  (wrong order)
		incl %esi							# Increase the specified digit count register

		cmp $0, %eax          # Compare %EAX with 0. Have we done enough division?
		jne positive_integer  # If not, loop once more.


	number_writer:
		popl %edx               # pop MSB to %EDX
		movb %dl, (%ebx)        # Move number to result.

		incl %ebx								# Increase Result pointer
		incl %ecx								# Increase counter

		decl %esi               # Decrease digit counter
		jnz number_writer      # If digit counter is not 0, repeat.

		# No more digits

		popl %edx								# Clean register
		incl %edx								# Point to next format.
		addl $4, %ebp           # Also point to next argument.

		jmp loop_master         # Return to main loop.


	hex:
		pushl %edx              # format pointer to stack.
		movl $0, %esi           # make %ESI digit counter again.

		movl (%ebp), %eax       # Store integer format in %EAX.


	make_hex:
		movl $0, %edx           # Empty %EDX. Divison will leave remainder here.
		movl $16, %edi          # Hex division, put 16 in Work Register
		divl %edi               # Divide %EAX by 16  ^

		cmp $9, %edx            # Remainder larger than 9?
		ja greater_than_nine    # If yes, jump to function

		# Less than 9
		addl $48, %edx          # add ASCII '0' to whats left.
		push %edx								# and push the number to the stack.
		incl %esi               # +1 digit

		cmp $0, %eax            # 0 left?
		jne make_hex            # No? repeat.

		jmp number_writer       # Yes? Write digit.




	zhex:
		movb $48, (%ebx) 	 # Copy '0' to result
		incl %ebx          # Point to next in result
		incl %ecx          # Increase counter.

		movb $120, (%ebx)   # Copy 'x' to result
		incl %ebx						# ..
		incl %ecx						# ..

		jmp hex





	greater_than_nine:
		addl $87, %edx          # add 87 to remainder. ASCII for 'a', hex for 10.
		push %edx 							# push sum to the stack.

		incl %esi               # +1 digit.

		cmp $0, %eax            # 0 left?
		jne make_hex            # No? repeat.

		jmp number_writer       # Yes? Write digit.


  # Increment Counter and pointers
	# to Result and format
	# Finally continue loop.
	increment:
		incl %edx
		incl %ebx
		incl %ecx
		jmp loop_master


	done:
	movb	$0, (%ebx) 		# Make %EBX ( result pointer ) trigger null-byte '\0'
	movl 	%ecx, %eax 		# Return number of bytes copied.

	# Reset work registers.
	popl 	%edi
	popl 	%esi
	popl 	%ebp

	ret 					# Finally return number of bytes copied.
