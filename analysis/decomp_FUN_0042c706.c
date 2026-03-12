// FUN_0042c706 @ 0042c706


void __cdecl
FUN_0042c706(undefined4 *param_1,int *param_2,int param_3,int param_4,uint param_5,int param_6,
            int param_7)

{
  int iVar1;
  int *piVar2;
  int *piVar3;
  int iVar4;
  undefined4 *puVar5;
  uint local_8;
  
  iVar4 = 0;
  local_8 = param_5;
  if ((int)param_5 <= param_6) {
    do {
      iVar1 = 0;
      if (0 < param_7) {
        piVar2 = (int *)(param_3 + iVar4 * 4);
        do {
          if (*(byte *)(iVar1 + param_4) == local_8) {
            *piVar2 = iVar1;
            iVar4 = iVar4 + 1;
            piVar2 = piVar2 + 1;
          }
          iVar1 = iVar1 + 1;
        } while (iVar1 < param_7);
      }
      local_8 = local_8 + 1;
    } while ((int)local_8 <= param_6);
  }
  piVar2 = param_2;
  for (iVar4 = 0x17; iVar4 != 0; iVar4 = iVar4 + -1) {
    *piVar2 = 0;
    piVar2 = piVar2 + 1;
  }
  iVar4 = 0;
  if (0 < param_7) {
    do {
      param_2[*(byte *)(iVar4 + param_4) + 1] = param_2[*(byte *)(iVar4 + param_4) + 1] + 1;
      iVar4 = iVar4 + 1;
    } while (iVar4 < param_7);
  }
  iVar4 = 0x16;
  piVar2 = param_2;
  do {
    piVar3 = piVar2 + 1;
    *piVar3 = *piVar3 + *piVar2;
    iVar4 = iVar4 + -1;
    piVar2 = piVar3;
  } while (iVar4 != 0);
  param_7 = 0;
  puVar5 = param_1;
  for (iVar4 = 0x17; iVar4 != 0; iVar4 = iVar4 + -1) {
    *puVar5 = 0;
    puVar5 = puVar5 + 1;
  }
  if ((int)param_5 <= param_6) {
    iVar4 = (param_6 - param_5) + 1;
    piVar2 = param_2 + param_5;
    do {
      iVar1 = param_7 + (piVar2[1] - *piVar2);
      param_7 = iVar1 * 2;
      iVar4 = iVar4 + -1;
      *(int *)(((int)param_1 - (int)param_2) + (int)piVar2) = iVar1 + -1;
      piVar2 = piVar2 + 1;
    } while (iVar4 != 0);
  }
  iVar4 = param_5 + 1;
  if (iVar4 <= param_6) {
    piVar2 = param_2 + iVar4;
    iVar4 = (param_6 - iVar4) + 1;
    piVar3 = param_1 + param_5;
    do {
      iVar1 = *piVar3;
      piVar3 = piVar3 + 1;
      *piVar2 = (iVar1 * 2 + 2) - *piVar2;
      piVar2 = piVar2 + 1;
      iVar4 = iVar4 + -1;
    } while (iVar4 != 0);
  }
  return;
}

