#include <elf.h>
#include <stdint.h>
#include <stdio.h>

#define offset_of(__type,__field) ((size_t)&(((__type *)NULL)->__field))

int main(int argc, char **argv)
{
	Elf64_Ehdr fhead;
	FILE *elf = NULL;

	if (argc < 2)
		return 1;

       	elf = fopen(argv[1], "r+");
	if (!elf) {
		fprintf(stderr, "Usage: %s <filename>", argv[0]);
		return 1;
	}

	if (fread(&fhead, sizeof(fhead), 1, elf) < 0) {
		perror("file header");
		fclose(elf);
		return 1;
	}

	if (fseek(elf, fhead.e_phoff, SEEK_SET) < 0) {
		perror("seek to program header descriptor");
		fclose(elf);
		return 1;
	}

	printf("[ ] Got %d program headers\n", fhead.e_phnum);
	for (int i = 0; i < fhead.e_phnum; ++i) {
		Elf64_Phdr phdr;
		if (fread(&phdr, sizeof(phdr), 1, elf) < 0) {
			perror("seek to program header");
			fclose(elf);
			return 1;
		}

#if 0
		printf("%p %p %p %p %p %p %p\n",
		  		phdr.p_offset,
		  		phdr.p_vaddr,
		  		phdr.p_paddr,
		  		phdr.p_filesz,
		  		phdr.p_memsz,
		  		phdr.p_flags,
		  		phdr.p_align);
#endif

		if (phdr.p_offset == 0ull &&
		    phdr.p_vaddr == 0ull &&
		    phdr.p_paddr == 0ull &&
		    phdr.p_filesz == 0ull &&
		    phdr.p_memsz == 0ull) {
			unsigned char newflags = phdr.p_flags | 0x1;
			printf("[+] Found stack pheader in position %d\n", i);
			printf("[ ] Changing attributes from %u to %u\n",
			       phdr.p_flags, newflags);

			if (fseek(elf, -(sizeof(phdr) - offset_of(Elf64_Phdr, p_flags)), SEEK_CUR) < 0) {
				perror("fseek back to flags");
				fclose(elf);
				return 1;
			}
			printf("addr: %p\n",ftell(elf));
			if (fwrite(&newflags, 1, 1, elf) < 0) {
				perror("writing new flags");
				fclose(elf);
				return 1;
			}

			break;
		}
	}

	if (fclose(elf) < 0) {
		perror("closing file");
		return 1;
	}

	printf("[+] Done!\n");

	return 0;
}
