// FUN_004292a0 @ 004292a0


void __cdecl FUN_004292a0(int param_1)

{
  int iVar1;
  
  *(undefined4 *)(param_1 + 0xc68) = 0;
  iVar1 = 0;
  do {
    if (*(char *)(param_1 + 0xc6c + iVar1) != '\0') {
      *(char *)(param_1 + 0xd7c + *(int *)(param_1 + 0xc68)) = (char)iVar1;
      *(int *)(param_1 + 0xc68) = *(int *)(param_1 + 0xc68) + 1;
    }
    iVar1 = iVar1 + 1;
  } while (iVar1 < 0x100);
  return;
}

