// === FUN_00005cf0 at 00005cf0 (250 bytes) ===

undefined4 FUN_00005cf0(int param_1,int param_2)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  undefined4 uVar7;
  undefined4 in_lr;
  
  iVar3 = DAT_00005df0;
  if (param_1 == 0) {
    if (param_2 == 0) {
      if (*DAT_00005df4 == '\0') {
        cVar1 = *DAT_00005df8;
        goto joined_r0x00005d56;
      }
    }
    else {
      cVar1 = *DAT_00005dfc;
joined_r0x00005d56:
      if (cVar1 == '\0') {
        *(undefined1 *)(DAT_00005df0 + 0x1b) = 0;
        *(undefined1 *)(iVar3 + 0x11) = 0;
        goto LAB_00005d00;
      }
    }
    iVar6 = DAT_00005df0 + 0xc4;
    cVar1 = *(char *)(DAT_00005df0 + 0x1b);
    if (cVar1 == '\0') {
      if (*(char *)(DAT_00005df0 + 0x11) == '\0') {
        *(undefined1 *)(DAT_00005df0 + 0x10) = 1;
      }
      else {
        iVar6 = FUN_00006b64(*(undefined4 *)(DAT_00005df0 + 0x1c),iVar6,4);
        if (iVar6 != 0) {
          *(undefined1 *)(iVar3 + 0x1b) = 2;
          *(undefined2 *)(iVar3 + 0x10) = 0;
        }
      }
    }
    else if (cVar1 == '\x01') {
      if (*(char *)(DAT_00005df0 + 0x11) != '\0') {
        if ((*DAT_00005e00 & 4) == 0) {
          FUN_00006b64(*(undefined4 *)(DAT_00005df0 + 0x1c),iVar6,4);
        }
        *(undefined1 *)(iVar3 + 0x1b) = 2;
        *(undefined1 *)(iVar3 + 0x11) = 0;
      }
    }
    else if (cVar1 == '\x02') {
      iVar4 = FUN_00006b48();
      iVar2 = DAT_00005dec;
      if (iVar4 != 0) {
        uVar5 = *(undefined4 *)(iVar3 + 0x1c);
        if ((*DAT_00005e00 & 4) == 0) {
          FUN_00006b64(uVar5,iVar6,4);
        }
        else {
          uVar7 = *(undefined4 *)(iVar3 + 0x3c);
          *(char *)(DAT_00005dec + 1) = (char)uVar7;
          *(char *)(iVar2 + 2) = (char)((uint)uVar7 >> 8);
          *(undefined1 *)(iVar2 + 3) = *(undefined1 *)(iVar3 + 3);
          *(undefined1 *)(iVar2 + 4) = *(undefined1 *)(iVar3 + 4);
          iVar6 = *(int *)(iVar3 + 0x40);
          *(char *)(iVar2 + 5) = (char)iVar6;
          *(char *)(iVar2 + 6) = (char)(((uint)(iVar6 >> 7) >> 0x18) + iVar6 >> 8);
          *(undefined1 *)(iVar2 + 7) = *(undefined1 *)(iVar3 + 7);
          *(undefined1 *)(iVar2 + 8) = *(undefined1 *)(iVar3 + 8);
          FUN_00006b64(uVar5,iVar2,9);
          *(undefined1 *)(iVar3 + 0x1b) = 5;
        }
      }
    }
    else if ((cVar1 == '\x05') && (iVar6 = FUN_00006b8c(), iVar6 != 0)) {
      FUN_0000571c(2);
      *(undefined1 *)(iVar3 + 0x1b) = 1;
    }
  }
  else {
    *(undefined1 *)(DAT_00005df0 + 0x1b) = 0;
LAB_00005d00:
    *(undefined1 *)(iVar3 + 0x10) = 1;
  }
  return in_lr;
}



// === FUN_00007d80 at 00007d80 (228 bytes) ===

undefined8 FUN_00007d80(undefined1 *param_1,uint param_2,undefined1 *param_3,char *param_4)

{
  undefined1 uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  char cVar7;
  undefined4 in_lr;
  undefined1 *local_40;
  undefined1 *local_3c;
  undefined1 local_30 [16];
  uint local_20;
  undefined1 *local_1c;
  char *local_18;
  
  local_18 = param_4;
  local_1c = param_3;
  local_20 = param_2;
  uVar5 = 0;
  cVar7 = *param_4;
  uVar6 = 0;
  local_40 = param_3;
  while ((cVar7 != '\0' && (uVar6 < 0xe))) {
    uVar2 = uVar6 + 1 & 0xff;
    cVar7 = cVar7 + -1;
    uVar1 = *local_40;
    if (((char)local_20 == '\x04') || ((local_20 & 0xff) == 2)) {
      *param_1 = uVar1;
      local_40 = local_40 + 1;
      param_1 = param_1 + 1;
      uVar6 = uVar2;
    }
    else {
      local_40 = local_40 + 1;
      local_3c = (undefined1 *)FUN_00007c68(uVar1);
      if ((local_3c == (undefined1 *)0x0) ||
         (uVar3 = FUN_00007bf8(*local_3c,uVar1), 0xe < (uVar6 + uVar3 + 1 & 0xffff))) {
        local_30[uVar5] = uVar1;
        uVar5 = uVar5 + 1 & 0xff;
      }
      else {
        *param_1 = uVar1;
        param_1 = param_1 + 1;
        uVar4 = 0;
        uVar6 = uVar2;
        if (uVar3 != 0) {
          for (; uVar6 = uVar2, uVar4 < uVar3; uVar4 = uVar4 + 1 & 0xff) {
            *param_1 = *local_3c;
            local_3c = local_3c + 1;
            param_1 = param_1 + 1;
            uVar2 = uVar2 + 1 & 0xff;
          }
        }
      }
    }
  }
  uVar2 = 0;
  if (uVar5 != 0) {
    for (; uVar2 < uVar5; uVar2 = uVar2 + 1 & 0xff) {
      local_1c[uVar2] = local_30[uVar2];
    }
  }
  *local_18 = (char)uVar5;
  return CONCAT44(in_lr,uVar6);
}



// === FUN_00007cc4 at 00007cc4 (186 bytes) ===

undefined8
FUN_00007cc4(undefined1 *param_1,byte param_2,char param_3,undefined1 *param_4,char *param_5)

{
  undefined1 uVar1;
  char cVar2;
  undefined4 uVar3;
  int iVar4;
  undefined1 *puVar5;
  byte bVar6;
  char unaff_r7;
  undefined4 in_lr;
  char local_28;
  
  local_28 = '\0';
  iVar4 = 1;
  if (0xe < param_2) {
    param_2 = 0xe;
  }
  bVar6 = 0;
  puVar5 = param_1;
  cVar2 = '\0';
  if (param_2 != 0) {
    for (; local_28 = cVar2, bVar6 < param_2; bVar6 = bVar6 + 1) {
      uVar1 = *puVar5;
      if ((param_3 == '\x04') || (param_3 == '\x02')) {
        *param_4 = uVar1;
LAB_00007d2e:
        param_4 = param_4 + 1;
        local_28 = local_28 + '\x01';
      }
      else if (iVar4 == 1) {
        unaff_r7 = FUN_00007bf8(puVar5[1],uVar1);
        param_1 = (undefined1 *)FUN_00007c1c(uVar1);
        if (param_1 != (undefined1 *)0x0) {
          iVar4 = 2;
          *param_4 = uVar1;
          goto LAB_00007d2e;
        }
        iVar4 = 0;
      }
      else {
        unaff_r7 = unaff_r7 + -1;
        if (iVar4 == 2) {
          *param_1 = uVar1;
          param_1 = param_1 + 1;
        }
        if (unaff_r7 == '\0') {
          iVar4 = 1;
        }
      }
      puVar5 = puVar5 + 1;
      cVar2 = local_28;
    }
  }
  *param_5 = local_28;
  if (unaff_r7 == '\0') {
    uVar3 = 1;
  }
  else {
    uVar3 = 2;
  }
  return CONCAT44(in_lr,uVar3);
}



// === FUN_00005e04 at 00005e04 (156 bytes) ===

undefined4 FUN_00005e04(uint param_1,uint param_2,uint param_3)

{
  char *pcVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 in_lr;
  undefined1 local_1c;
  
  local_1c = 0x30;
  if (6 < param_3) {
    return in_lr;
  }
  *DAT_00005ea0 = 1;
  pcVar1 = DAT_00005ea4;
  *DAT_00005ea4 = '\0';
  *DAT_00005ea8 = 1;
  iVar2 = DAT_00005eb0;
  iVar3 = DAT_00005eac + param_3 * 9;
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar3,9);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  if (3 < param_2) {
    param_2 = 3;
  }
  if (param_1 == 0) {
LAB_00005e66:
    if (2 < param_1) goto LAB_00005e8c;
  }
  else if (param_1 == 1) {
    local_1c = 0x40;
  }
  else {
    if (param_1 != 2) goto LAB_00005e66;
    local_1c = 0x50;
  }
  *(undefined1 *)(iVar2 + 0xd) = local_1c;
  *(byte *)(iVar2 + 0xe) = (byte)param_2 | 8;
  do {
    iVar3 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 0xc,3);
    if (iVar3 != 0) break;
  } while (*pcVar1 == '\0');
LAB_00005e8c:
  if (*pcVar1 != '\0') {
    *DAT_00005eb4 = DAT_00005eb8;
  }
  return in_lr;
}



// === FUN_00008970 at 00008970 (88 bytes) ===

void FUN_00008970(int param_1,uint param_2,int param_3,uint param_4)

{
  uint uVar1;
  
  uVar1 = param_2 * 2;
  if (uVar1 < 0xffe00001) {
    uVar1 = param_4 * 2;
  }
  if (0xffe00000 < uVar1) {
    *DAT_0000896c = *DAT_0000896c | 1;
    return;
  }
  if ((param_1 == 0 && (param_2 & 0x7fffffff) == 0) && (param_3 == 0 && (param_4 & 0x7fffffff) == 0)
     ) {
    return;
  }
  if (-1 < (int)(param_2 | param_4)) {
    return;
  }
  return;
}



// === FUN_00005ebc at 00005ebc (54 bytes) ===

undefined4 FUN_00005ebc(void)

{
  byte bVar1;
  byte *pbVar2;
  undefined4 in_lr;
  
  if (*DAT_00005ef4 != '\0') {
    *DAT_00005ef4 = '\0';
    *DAT_00005ef8 = 1;
    *DAT_00005efc = 1;
    pbVar2 = DAT_00005f00;
    bVar1 = *DAT_00005f00;
    *DAT_00005f00 = bVar1 + 1;
    if (6 < (byte)(bVar1 + 1)) {
      *pbVar2 = 0;
    }
    FUN_00005e04(0,0,*pbVar2);
  }
  return in_lr;
}



// === FUN_00006b9c at 00006b9c (54 bytes) ===

undefined8 FUN_00006b9c(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 in_lr;
  
  iVar1 = FUN_00006b48();
  if (iVar1 != 0) {
    *(undefined4 *)(param_1 + 0x120) = 0;
    *(undefined4 *)(param_1 + 0x108) = param_3;
    *(undefined4 *)(param_1 + 0x10c) = param_4;
    *(undefined4 *)(param_1 + 0x100) = param_2;
    *(undefined4 *)(param_1 + 0x104) = param_4;
    *(undefined4 *)(param_1 + 0x120) = 0x101;
    iVar1 = 1;
  }
  return CONCAT44(in_lr,iVar1);
}



// === FUN_00007c1c at 00007c1c (54 bytes) ===

undefined4 FUN_00007c1c(uint param_1)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  if (param_1 < 0x4b) {
    uVar1 = *(undefined4 *)(DAT_00007c54 + param_1 * 4);
  }
  else {
    iVar2 = DAT_00007cb4;
    iVar3 = DAT_00007c58;
    if (((0x95 < param_1) && (iVar2 = DAT_00007cb8, iVar3 = DAT_00007c5c, 0xb8 < param_1)) &&
       (iVar2 = DAT_00007cc0, iVar3 = DAT_00007c64, param_1 < 0xdc)) {
      iVar2 = DAT_00007cbc;
      iVar3 = DAT_00007c60;
    }
    uVar1 = *(undefined4 *)(iVar3 + param_1 * 4 + iVar2);
  }
  return uVar1;
}



// === FUN_00007c68 at 00007c68 (54 bytes) ===

undefined4 FUN_00007c68(uint param_1)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  if (param_1 < 0x4b) {
    uVar1 = *(undefined4 *)(DAT_00007ca0 + param_1 * 4);
  }
  else {
    iVar2 = DAT_00007cb4;
    iVar3 = DAT_00007ca4;
    if (((0x95 < param_1) && (iVar2 = DAT_00007cb8, iVar3 = DAT_00007ca8, 0xb8 < param_1)) &&
       (iVar2 = DAT_00007cc0, iVar3 = DAT_00007cb0, param_1 < 0xdc)) {
      iVar2 = DAT_00007cbc;
      iVar3 = DAT_00007cac;
    }
    uVar1 = *(undefined4 *)(iVar3 + param_1 * 4 + iVar2);
  }
  return uVar1;
}



// === FUN_00008908 at 00008908 (52 bytes) ===

void FUN_00008908(int param_1,uint param_2,int param_3,uint param_4)

{
  if (param_1 != param_3) {
    return;
  }
  if (param_1 != 0 || ((param_2 | param_4) & 0x7fffffff) != 0) {
    if (param_2 == param_4) {
      return;
    }
    return;
  }
  return;
}



// === FUN_00004114 at 00004114 (48 bytes) ===

undefined4 FUN_00004114(void)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 in_lr;
  
  puVar1 = DAT_00004148;
  puVar3 = DAT_00004144;
  if (DAT_00004144 < DAT_00004148) {
    for (; puVar3 < puVar1; puVar3 = puVar3 + 3) {
      iVar2 = puVar3[1];
      if (puVar3[2] == iVar2) {
        FUN_0000854c(iVar2,0);
      }
      else {
        FUN_00008530(iVar2,puVar3[2],*puVar3);
      }
    }
  }
  return in_lr;
}



// === FUN_00006b64 at 00006b64 (40 bytes) ===

undefined8 FUN_00006b64(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 in_lr;
  
  iVar1 = FUN_00006b48();
  if (iVar1 != 0) {
    *(undefined4 *)(param_1 + 0x120) = 0x100;
    *(undefined4 *)(param_1 + 0x108) = param_2;
    *(undefined4 *)(param_1 + 0x10c) = param_3;
    iVar1 = 1;
  }
  return CONCAT44(in_lr,iVar1);
}



// === FUN_00007bf8 at 00007bf8 (34 bytes) ===

undefined4 FUN_00007bf8(undefined4 param_1,uint param_2)

{
  if (param_2 < 0x4b) {
    param_1 = 1;
  }
  else if (param_2 < 0x96) {
    param_1 = 2;
  }
  else if (param_2 < 0xb9) {
    param_1 = 3;
  }
  else if (param_2 < 0xdc) {
    param_1 = 4;
  }
  return param_1;
}



// === FUN_0000571c at 0000571c (26 bytes) ===

void FUN_0000571c(int param_1)

{
  undefined4 uVar1;
  
  if (param_1 == 1) {
    uVar1 = 0x100;
  }
  else {
    if (param_1 != 2) {
      return;
    }
    uVar1 = 0x200;
  }
  *DAT_00005738 = uVar1;
  return;
}



// === FUN_00008530 at 00008530 (26 bytes) ===

void FUN_00008530(undefined1 *param_1,undefined1 *param_2,int param_3)

{
  undefined1 uVar1;
  
  if (param_3 != 0) {
    do {
      uVar1 = *param_2;
      param_2 = param_2 + 1;
      *param_1 = uVar1;
      param_1 = param_1 + 1;
      param_3 = param_3 + -1;
    } while (param_3 != 0);
  }
  return;
}

