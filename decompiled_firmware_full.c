// === FUN_000050f0 at 000050f0 (1234 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000050f0(void)

{
  char *pcVar1;
  byte bVar2;
  char cVar3;
  undefined1 uVar4;
  undefined2 uVar5;
  uint uVar6;
  uint *puVar7;
  undefined4 uVar8;
  undefined1 extraout_r1;
  undefined1 extraout_r1_00;
  uint uVar9;
  uint extraout_r1_01;
  int extraout_r1_02;
  int extraout_r1_03;
  uint extraout_r1_04;
  int extraout_r1_05;
  int extraout_r1_06;
  undefined4 uVar10;
  int extraout_r1_07;
  int extraout_r1_08;
  undefined1 *puVar11;
  undefined1 *puVar12;
  int iVar13;
  uint uVar14;
  uint uVar15;
  int iVar16;
  code *UNRECOVERED_JUMPTABLE;
  undefined8 uVar17;
  undefined1 uStack_28;
  undefined1 uStack_27;
  undefined1 uStack_26;
  undefined1 uStack_25;
  uint uStack_24;
  uint uStack_20;
  uint uStack_1c;
  uint uStack_18;
  
  pcVar1 = _DAT_000053c4;
  puVar11 = &uStack_28;
  puVar12 = &uStack_28;
  uStack_26 = 0;
  uStack_25 = 0;
  if (_DAT_000053c8 <= *(int *)(_DAT_000053c4 + 0x4c)) {
    pcVar1[0x4c] = '\0';
    pcVar1[0x4d] = '\0';
    pcVar1[0x4e] = '\0';
    pcVar1[0x4f] = '\0';
  }
  iVar16 = *(int *)(pcVar1 + 0x4c);
  *(int *)(pcVar1 + 0x4c) = iVar16 + 1;
  uStack_18 = FUN_0000497c(*_DAT_000053cc);
  uVar15 = *_DAT_000053d0;
  if (uVar15 < 1000) {
    uStack_28 = 0;
    uVar4 = 0;
    if (899 < uVar15) {
LAB_00005164:
      func_0x00008574((uVar15 + _DAT_000053e4) * 0x13,500);
      puVar12[1] = extraout_r1_00;
      uVar4 = uStack_27;
    }
  }
  else {
    if (uVar15 < _DAT_000053d4) {
      func_0x00008574((uVar15 + _DAT_000053d8) * 0xc,_DAT_000053dc);
      *puVar11 = extraout_r1;
      if (uVar15 < _DAT_000053e0) goto LAB_00005164;
    }
    else {
      uStack_28 = 0xc;
    }
    uVar4 = 0x13;
  }
  uStack_27 = uVar4;
  uVar6 = (uint)*_DAT_000053e8;
  iVar13 = *_DAT_000053ec;
  if ((uint)*_DAT_000053f0 < *_DAT_000053f4) {
    uVar9 = uVar6 + iVar13;
    if (uVar6 < 10) {
      uVar9 = 10;
    }
  }
  else {
    uVar9 = iVar13 + uVar6;
  }
  uVar6 = uVar6 + iVar13;
  *(uint *)(pcVar1 + 0x28) = uVar6;
  if ((byte)pcVar1[7] + 1 < uVar9) {
    uVar9 = (byte)pcVar1[7] + 1;
  }
  uVar14 = (uint)*_DAT_000053f8;
  if (uVar14 < uVar6) {
    uStack_20 = 0x13;
  }
  else {
    func_0x00008574(uVar6 * 0x13,uVar14);
    uStack_20 = extraout_r1_01 & 0xff;
  }
  uVar6 = (uint)*_DAT_000053fc;
  if (uVar14 + uVar6 < uVar9) {
    uVar6 = 0x13;
  }
  else if (uVar9 < uVar6) {
    uVar6 = 0;
  }
  else {
    func_0x00008574(uVar9 * 0x13,uVar14);
    iVar13 = extraout_r1_02;
    func_0x00008584(uVar6 * 0x13,uVar14);
    uVar6 = iVar13 - extraout_r1_03;
  }
  pcVar1[7] = (char)uVar9;
  if (*_DAT_000053f4 < 0x65) {
    func_0x00008574(*_DAT_000053f4 * 0x13,100);
    uStack_1c = extraout_r1_04 & 0xff;
  }
  else {
    uStack_1c = 0x13;
  }
  iVar16 = func_0x00008584(iVar16 + 1,0xfa);
  if (iVar16 == 0) {
    bVar2 = func_0x0000499c();
    *_DAT_00005400 = bVar2;
  }
  uStack_24 = FUN_0000506c();
  func_0x00004818();
  uVar9 = FUN_00004d38(uStack_18 & 0xff,uStack_24 & 0xff,*_DAT_00005404,uStack_1c & 0xff,
                       uStack_20 & 0xff);
  if (*(uint *)(pcVar1 + 0x2c) < uVar9) {
    uVar9 = *(uint *)(pcVar1 + 0x2c);
  }
  if ((int)uVar9 < 0x400) {
    uVar9 = 0x400;
  }
  *_DAT_00005408 = uVar9;
  if ((*(uint *)(pcVar1 + 0x14) < uVar15) && (2 < *_DAT_000053f4)) {
    pcVar1[0x14] = -0x44;
    pcVar1[0x15] = '\x02';
    pcVar1[0x16] = '\0';
    pcVar1[0x17] = '\0';
  }
  else if ((uVar15 < _DAT_0000540c) || (*_DAT_00005410 < 0x1f)) {
    pcVar1[0x14] = -0x18;
    pcVar1[0x15] = '\x03';
    pcVar1[0x16] = '\0';
    pcVar1[0x17] = '\0';
    cVar3 = '\0';
    goto LAB_000052aa;
  }
  cVar3 = '\x01';
LAB_000052aa:
  pcVar1[6] = cVar3;
  iVar16 = FUN_00004b38(uStack_20 & 0xff,uStack_24 & 0xff,*_DAT_00005404,*_DAT_000053f4 & 0xff,
                        uVar15,uStack_1c & 0xff,uStack_27);
  func_0x00008574((uint)*_DAT_00005400 * iVar16,100);
  uVar9 = iVar16 - extraout_r1_05;
  if (pcVar1[9] != '\0') {
    pcVar1[10] = '\x01';
    iVar13 = *_DAT_00005404;
    iVar16 = FUN_000048e8(uStack_28,uStack_24 & 0xff);
    uVar9 = iVar13 + iVar16;
  }
  if (0xfff < uVar9) {
    uVar9 = 0xfff;
  }
  *_DAT_000053cc = uVar9;
  iVar16 = FUN_00004a94(uVar6 & 0xff,uStack_28,uStack_24 & 0xff);
  func_0x00008574((uint)*_DAT_00005400 * iVar16,100);
  uVar9 = iVar16 - extraout_r1_06;
  uVar6 = uVar9;
  if ((((uint)(byte)pcVar1[0xf] * 3 + (uint)(byte)pcVar1[0x10] < (uStack_24 & 0xff)) && (uVar9 != 0)
      ) && (uVar15 <= *_DAT_00005614)) {
    if ((0xc7f < uVar15) && (*_DAT_00005618 != '\0')) {
      uStack_26 = 1;
      uVar6 = 0x19a;
      if ((0x199 < uVar9) && (uVar6 = uVar9, _DAT_0000561c <= uVar9)) {
        uVar6 = _DAT_0000561c - 1;
      }
    }
    iVar16 = func_0x00006fa0(_DAT_00005620,uVar6 * 0x18 + 3);
    if ((iVar16 != 0) && (uStack_25 = 1, *_DAT_00005624 != '\0')) {
      *_DAT_00005628 = 1;
    }
  }
  *_DAT_0000562c = uStack_26;
  *_DAT_00005630 = uStack_25;
  puVar11 = _DAT_00005634;
  if (*_DAT_00005638 == '\0') {
    uVar15 = *_DAT_00005408;
    puVar7 = _DAT_000053cc;
  }
  else {
    uVar15 = *_DAT_00005640;
    puVar7 = _DAT_0000563c;
  }
  uVar9 = *puVar7;
  *_DAT_00005634 = (char)uVar9;
  puVar11[1] = (char)(uVar9 >> 8);
  iVar16 = FUN_0000495c();
  *_DAT_00005644 = (char)iVar16;
  puVar11 = _DAT_00005648;
  *_DAT_00005648 = (char)(uVar15 * 100 >> 7);
  puVar11[1] = (char)(uVar15 * 100 >> 0xf);
  puVar11 = _DAT_0000564c;
  uVar10 = *_DAT_00005650;
  *_DAT_0000564c = (char)uVar10;
  puVar11[1] = (char)((uint)uVar10 >> 8);
  *_DAT_00005654 = (char)*(undefined4 *)(pcVar1 + 0x28);
  func_0x00008574(iVar16 * *_DAT_00005658,100);
  iVar16 = extraout_r1_07;
  func_0x00008574(uVar6 * *_DAT_0000565c,_DAT_00005660);
  *(uint *)(pcVar1 + 0x50) = *_DAT_00005664 * (iVar16 + extraout_r1_08) * 3;
  uVar17 = func_0x00007120();
  func_0x00007128((int)uVar17,(int)((ulonglong)uVar17 >> 0x20),0,_DAT_00005668);
  uVar8 = func_0x00007138();
  uVar17 = func_0x00007160();
  iVar16 = func_0x00005704(0,0,(int)uVar17,(int)((ulonglong)uVar17 >> 0x20));
  uVar10 = _DAT_00005674;
  if (iVar16 != 0) {
    uVar17 = func_0x00007120(*_DAT_0000566c);
    func_0x00007128((int)uVar17,(int)((ulonglong)uVar17 >> 0x20),0,_DAT_00005670);
    uVar10 = func_0x00007138();
    func_0x000056fc(uVar10,uVar8);
    func_0x00007160();
    uVar10 = func_0x00007138();
  }
  func_0x00005f04(_DAT_00005678,uVar10);
  uVar15 = func_0x00007150();
  if (_DAT_0000567c <= uVar15) {
    uVar15 = _DAT_0000567c - 1;
  }
  uVar5 = func_0x00004674(pcVar1 + 0x5c,uVar15);
  uVar10 = *_DAT_00005680;
  uVar17 = func_0x00007160(uVar10);
  iVar16 = func_0x00005704(0,0,(int)uVar17,(int)((ulonglong)uVar17 >> 0x20));
  if (iVar16 != 0) {
    func_0x000056fc(*_DAT_00005684,uVar10);
  }
  uVar10 = func_0x00005714();
  puVar11 = _DAT_00005688;
  *_DAT_00005688 = (char)uVar10;
  puVar11[1] = (char)((uint)uVar10 >> 8);
  puVar11[2] = (char)((uint)uVar10 >> 0x10);
  puVar11 = _DAT_00005690;
  uVar10 = *_DAT_0000568c;
  *_DAT_00005690 = (char)uVar10;
  puVar11[1] = (char)((uint)uVar10 >> 8);
  puVar11 = _DAT_00005694;
  *_DAT_00005694 = (char)uVar5;
  puVar11[1] = (char)((ushort)uVar5 >> 8);
  *_DAT_00005698 = (char)*_DAT_0000569c;
  puVar11 = _DAT_000056a4;
  uVar10 = *_DAT_000056a0;
  *_DAT_000056a4 = (char)uVar10;
  puVar11[1] = (char)((uint)uVar10 >> 8);
  puVar11 = _DAT_000056a8;
  iVar16 = *_DAT_000056ec;
  *_DAT_000056a8 = (char)(iVar16 + 0x28);
  puVar11[1] = (char)((uint)(iVar16 + 0x28) >> 8);
  puVar11 = _DAT_000056ac;
  uVar15 = *_DAT_00005664;
  *_DAT_000056ac = (char)uVar15;
  puVar11[1] = (char)(uVar15 >> 8);
  uVar15 = *_DAT_000056b0;
  if (0xff < uVar15) {
    uVar15 = 0xff;
  }
  *_DAT_000056b4 = (char)uVar15;
  if (*_DAT_000056b8 == '\x01') {
    uVar4 = func_0x00004650(pcVar1 + 0xdc,*_DAT_000056bc);
  }
  else {
    uVar4 = *_DAT_000056bc;
  }
  *_DAT_000056c0 = uVar4;
  iVar16 = *_DAT_000056c4 + 0x28;
  if (iVar16 < 0) {
    iVar16 = 0;
  }
  *_DAT_000056c8 = (char)iVar16;
  *_DAT_0000566c = *_DAT_000056f0;
  *_DAT_000056cc = (char)*_DAT_000056f4;
  *_DAT_000056d0 = *_DAT_000056d4;
  puVar11 = _DAT_000056d8;
  uVar4 = FUN_000046d0(*_DAT_00005664);
  *puVar11 = uVar4;
  uVar4 = func_0x00004698();
  *_DAT_000056dc = uVar4;
  if (((*(uint *)(pcVar1 + 0x18) == *_DAT_00005664) && (*(int *)(pcVar1 + 0x1c) == *_DAT_000056e0))
     && (_DAT_000056e4 <= *_DAT_00005664)) {
    uVar15 = *(int *)(pcVar1 + 0x24) + 1;
  }
  else {
    uVar15 = 0;
  }
  *(uint *)(pcVar1 + 0x24) = uVar15;
  if (_DAT_000056e8 <= uVar15) {
    FUN_000074e8();
    *pcVar1 = *pcVar1 + '\x01';
    pcVar1[0x24] = '\0';
    pcVar1[0x25] = '\0';
    pcVar1[0x26] = '\0';
    pcVar1[0x27] = '\0';
  }
  *(uint *)(pcVar1 + 0x18) = *_DAT_00005664;
  *(int *)(pcVar1 + 0x1c) = *_DAT_000056e0;
  *(undefined4 *)(pcVar1 + 0x20) = *_DAT_000056f8;
                    /* WARNING: Could not recover jumptable at 0x00005610. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)(uStack_24 & 0xff);
  return;
}



// === FUN_000081a8 at 000081a8 (854 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000081a8(void)

{
  undefined1 uVar1;
  undefined1 *puVar2;
  char cVar3;
  int iVar4;
  undefined1 *puVar5;
  undefined1 *puVar6;
  undefined4 uVar7;
  undefined1 *puVar8;
  code *UNRECOVERED_JUMPTABLE;
  
  uVar7 = 7;
  iVar4 = func_0x00007b04();
  puVar2 = _DAT_00008500;
  if (iVar4 == 0) goto LAB_000084f4;
  uVar7 = 0;
  puVar8 = _DAT_00008500 + 200;
  if (_DAT_00008500[9] != '\0') {
    FUN_00007eb4(puVar8,2,_DAT_00008500 + 0x58,_DAT_00008500 + 0x24);
    cVar3 = func_0x00007bf0(puVar8);
    FUN_00007af8(puVar8,cVar3 + '\x01');
    puVar2[9] = 0;
    uVar7 = 8;
    goto LAB_000084f4;
  }
  if (_DAT_00008500[8] == '\0') {
    if (_DAT_00008500[7] == '\0') {
      if (_DAT_00008500[0xc] == '\0') {
        if (_DAT_00008500[0xb] == '\0') {
          if (_DAT_00008500[0xf] == '\0') {
            if (_DAT_00008500[0xe] == '\0') {
              uVar1 = _DAT_00008500[0x13];
              puVar5 = _DAT_00008500 + 0x98;
              puVar6 = _DAT_00008500 + 0x88;
              if ((_DAT_00008500[0x11] & 1 & _DAT_00008500[0x12] == '\0') == 0) {
                if (_DAT_00008500[0x10] == '\0') {
                  uVar1 = _DAT_00008500[0x18];
                  puVar5 = _DAT_00008500 + 0xb8;
                  puVar6 = _DAT_00008500 + 0xa8;
                  if ((_DAT_00008500[0x16] & 1 & _DAT_00008500[0x17] == '\0') == 0) {
                    if (_DAT_00008500[0x15] == '\0') goto LAB_000084f4;
                    _DAT_00008500[0x15] = 0;
                    *puVar2 = 0;
                    puVar2[2] = 0;
                    puVar2[5] = 0;
                    func_0x00007fd8(puVar5,puVar2 + 0x19,puVar6,uVar1);
                    FUN_00007eb4(puVar8,4,puVar6,puVar2 + 0x18);
                    cVar3 = func_0x00007bf0(puVar8);
                    FUN_00007af8(puVar8,cVar3 + '\x01');
                    func_0x00007b38();
                    if (puVar2[0x18] == '\0') {
                      puVar2[5] = 1;
                      uVar7 = 0x11;
                    }
                    else {
                      uVar7 = 0x12;
                    }
                    puVar2[0x16] = 1;
                  }
                  else {
                    func_0x00007fd8(puVar5,_DAT_00008500 + 0x19,puVar6,uVar1);
                    FUN_00007eb4(puVar8,4,puVar6,puVar2 + 0x18);
                    cVar3 = func_0x00007bf0(puVar8);
                    FUN_00007af8(puVar8,cVar3 + '\x01');
                    func_0x00007b38();
                    if ((puVar2[0x18] == '\0') || (puVar2[0x18] == puVar2[0x1e])) {
                      puVar2[5] = 1;
                      uVar7 = 0x11;
                    }
                    else {
                      uVar7 = 0x12;
                    }
                  }
                  puVar2[0x17] = 1;
                  func_0x00007f58(puVar5,puVar2 + 0x19,puVar6);
                  puVar2[0x1e] = puVar2[0x18];
                  goto LAB_000084f4;
                }
                _DAT_00008500[0x10] = 0;
                puVar2[1] = 0;
                puVar2[3] = 0;
                puVar2[4] = 0;
                func_0x00007fd8(puVar5,puVar2 + 0x14,puVar6,uVar1);
                FUN_00007eb4(puVar8,0,puVar6,puVar2 + 0x13);
                cVar3 = func_0x00007bf0(puVar8);
                FUN_00007af8(puVar8,cVar3 + '\x01');
                func_0x00007b4c();
                if (puVar2[0x13] == '\0') {
                  puVar2[4] = 1;
                  uVar7 = 0xf;
                }
                else {
                  uVar7 = 0x10;
                }
                puVar2[0x11] = 1;
              }
              else {
                func_0x00007fd8(puVar5,_DAT_00008500 + 0x14,puVar6,uVar1);
                FUN_00007eb4(puVar8,0,puVar6,puVar2 + 0x13);
                cVar3 = func_0x00007bf0(puVar8);
                FUN_00007af8(puVar8,cVar3 + '\x01');
                func_0x00007b4c();
                if ((puVar2[0x13] == '\0') || (puVar2[0x13] == puVar2[0x1d])) {
                  puVar2[4] = 1;
                  uVar7 = 0xf;
                }
                else {
                  uVar7 = 0x10;
                }
              }
              puVar2[0x12] = 1;
              func_0x00007f58(puVar5,puVar2 + 0x14,puVar6);
              puVar2[0x1d] = puVar2[0x13];
              goto LAB_000084f4;
            }
            _DAT_00008500[0xe] = 0;
            FUN_00007eb4(puVar8,3,puVar2 + 0x78,puVar2 + 0xd);
            cVar3 = func_0x00007bf0(puVar8);
            FUN_00007af8(puVar8,cVar3 + '\x01');
            cVar3 = puVar2[0xd];
            if (cVar3 != '\0') {
              puVar2[0xf] = 1;
              goto LAB_00008312;
            }
          }
          else {
            FUN_00007eb4(puVar8,3,_DAT_00008500 + 0x78,_DAT_00008500 + 0xd);
            cVar3 = func_0x00007bf0(puVar8);
            FUN_00007af8(puVar8,cVar3 + '\x01');
            cVar3 = puVar2[0xd];
            if ((cVar3 != '\0') && (cVar3 != puVar2[0x1c])) {
LAB_00008312:
              puVar2[0x1c] = cVar3;
              uVar7 = 0xe;
              goto LAB_000084f4;
            }
            puVar2[0xf] = 0;
          }
          uVar7 = 0xd;
          goto LAB_000084f4;
        }
        _DAT_00008500[0xb] = 0;
        FUN_00007eb4(puVar8,1,puVar2 + 0x68,puVar2 + 10);
        cVar3 = func_0x00007bf0(puVar8);
        FUN_00007af8(puVar8,cVar3 + '\x01');
        cVar3 = puVar2[10];
        if (cVar3 != '\0') {
          puVar2[0xc] = 1;
          goto LAB_0000829c;
        }
      }
      else {
        FUN_00007eb4(puVar8,1,_DAT_00008500 + 0x68,_DAT_00008500 + 10);
        cVar3 = func_0x00007bf0(puVar8);
        FUN_00007af8(puVar8,cVar3 + '\x01');
        cVar3 = puVar2[10];
        if ((cVar3 != '\0') && (cVar3 != puVar2[0x1b])) {
LAB_0000829c:
          puVar2[0x1b] = cVar3;
          uVar7 = 0xc;
          goto LAB_000084f4;
        }
        puVar2[0xc] = 0;
      }
      uVar7 = 0xb;
      goto LAB_000084f4;
    }
    _DAT_00008500[7] = 0;
    FUN_00007eb4(puVar8,5,puVar2 + 0x48,puVar2 + 6);
    cVar3 = func_0x00007bf0(puVar8);
    FUN_00007af8(puVar8,cVar3 + '\x01');
    cVar3 = puVar2[6];
    if (cVar3 != '\0') {
      puVar2[8] = 1;
      goto LAB_00008228;
    }
  }
  else {
    FUN_00007eb4(puVar8,5,_DAT_00008500 + 0x48,_DAT_00008500 + 6);
    cVar3 = func_0x00007bf0(puVar8);
    FUN_00007af8(puVar8,cVar3 + '\x01');
    cVar3 = puVar2[6];
    if ((cVar3 != '\0') && (cVar3 != puVar2[0x1a])) {
LAB_00008228:
      puVar2[0x1a] = cVar3;
      uVar7 = 10;
      goto LAB_000084f4;
    }
    puVar2[8] = 0;
  }
  uVar7 = 9;
LAB_000084f4:
                    /* WARNING: Could not recover jumptable at 0x000084fc. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)(uVar7);
  return;
}



// === FUN_00004d38 at 00004d38 (734 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00004d38(undefined4 param_1,int param_2,undefined4 param_3,int param_4,byte param_5)

{
  byte bVar1;
  byte bVar2;
  byte *pbVar3;
  int iVar4;
  int extraout_r1;
  int extraout_r1_00;
  int extraout_r1_01;
  int extraout_r1_02;
  int extraout_r1_03;
  int extraout_r1_04;
  int extraout_r1_05;
  int extraout_r1_06;
  int extraout_r1_07;
  int extraout_r1_08;
  int extraout_r1_09;
  int extraout_r1_10;
  int extraout_r1_11;
  int iVar5;
  int extraout_r1_12;
  int extraout_r1_13;
  uint extraout_r1_14;
  int extraout_r1_15;
  uint extraout_r1_16;
  int iVar6;
  int iVar7;
  uint uVar8;
  int iVar9;
  int unaff_r5;
  int iVar10;
  code *UNRECOVERED_JUMPTABLE;
  byte bStack_2b;
  int iStack_28;
  int iStack_24;
  int iStack_20;
  int iStack_18;
  
  iVar6 = _DAT_00005018;
  bVar1 = *(byte *)(_DAT_00005018 + 0xf);
  bVar2 = *(byte *)(_DAT_00005018 + 0x10);
  iVar7 = 0;
  if (*(char *)(_DAT_00005018 + 2) != '\0') {
    if ((((*_DAT_0000501c == '\0') && (*_DAT_00005020 == '\0')) && (*_DAT_00005024 == '\0')) &&
       (*_DAT_00005028 == '\0')) {
      *(undefined1 *)(_DAT_00005018 + 1) = 1;
    }
    else {
      *(undefined1 *)(_DAT_00005018 + 1) = 0;
    }
    *(undefined1 *)(iVar6 + 2) = 0;
  }
  pbVar3 = _DAT_0000502c;
  iVar10 = *_DAT_00005054;
  if (((int)((uint)bVar1 + (uint)bVar2) < param_2) && (*(char *)(iVar6 + 0xe) != '\0')) {
    uVar8 = *_DAT_00005058;
    if (*(char *)(iVar6 + 1) == '\0') {
      iStack_20 = (int)*(char *)(_DAT_0000504c + (uint)param_5 * 0x14 + param_4);
      bVar1 = *_DAT_00005050;
      bVar2 = *_DAT_0000505c;
      func_0x00008584((uint)bVar1 * (uint)bVar2 * 0x80,1000);
      func_0x00008584((uint)bVar1 << 7,10);
      func_0x00008574((uint)bVar2 * *(int *)(iVar6 + 0x48),100);
      *(undefined4 *)(iVar6 + 0x2c) = *(undefined4 *)(iVar6 + 0x44);
      if ((bVar2 < pbVar3[3]) && (*(int *)(iVar6 + 0x48) != 0)) {
        iVar9 = 1;
        if (*_DAT_00005060 < 0x33) {
          bStack_2b = (byte)iVar7;
        }
        else {
          bStack_2b = 0x80;
        }
      }
      else {
        iVar9 = 0;
      }
      iStack_18 = extraout_r1_06;
      if (uVar8 < 1000) {
        iVar5 = 0;
        unaff_r5 = 0;
        iVar9 = iVar7;
        iStack_28 = iVar7;
        iStack_24 = iVar7;
      }
      else if (uVar8 < _DAT_00005064) {
        func_0x00008574(uVar8 + _DAT_00005030,5);
        unaff_r5 = *(int *)(iVar6 + 0x34) - iVar10;
        iVar5 = extraout_r1_07;
        iStack_28 = iVar7;
        iStack_24 = iVar7;
        if (uVar8 < 0x4b0) {
          iVar9 = 0;
        }
      }
      else {
        iStack_28 = extraout_r1_04;
        iStack_24 = extraout_r1_05;
        if (uVar8 < 2000) {
          func_0x00008574(uVar8 + _DAT_00005034,5);
          unaff_r5 = *(int *)(iVar6 + 0x38) - *(int *)(iVar6 + 0x34);
          iVar10 = *(int *)(iVar6 + 0x34);
          iVar5 = extraout_r1_08;
        }
        else if (uVar8 < _DAT_00005038) {
          func_0x00008574(uVar8 + _DAT_0000503c,5);
          unaff_r5 = *(int *)(iVar6 + 0x3c) - *(int *)(iVar6 + 0x38);
          iVar10 = *(int *)(iVar6 + 0x38);
          iVar5 = extraout_r1_09;
        }
        else if (uVar8 < _DAT_00005068) {
          func_0x00008574(uVar8 + _DAT_00005040,5);
          unaff_r5 = *(int *)(iVar6 + 0x40) - *(int *)(iVar6 + 0x3c);
          iVar10 = *(int *)(iVar6 + 0x3c);
          iVar5 = extraout_r1_10;
        }
        else if (uVar8 < _DAT_00005044) {
          func_0x00008574(uVar8 + _DAT_00005048,5);
          unaff_r5 = *(int *)(iVar6 + 0x44) - *(int *)(iVar6 + 0x40);
          iVar10 = *(int *)(iVar6 + 0x40);
          iVar5 = extraout_r1_11;
        }
        else {
          iVar5 = 0;
          iVar10 = *(int *)(iVar6 + 0x44);
          iStack_28 = extraout_r1_05;
        }
      }
    }
    else {
      *(undefined4 *)(iVar6 + 0x2c) = 0xf00;
      iStack_20 = 0;
      iStack_28 = 0;
      iStack_24 = 0;
      iVar9 = 0;
      if (0x180 < *(uint *)(iVar6 + 0x34)) {
        *(undefined4 *)(iVar6 + 0x34) = 0x180;
      }
      if (0x200 < *(uint *)(iVar6 + 0x38)) {
        *(undefined4 *)(iVar6 + 0x38) = 0x200;
      }
      if (0x280 < *(uint *)(iVar6 + 0x3c)) {
        *(undefined4 *)(iVar6 + 0x3c) = 0x280;
      }
      if (0x300 < *(uint *)(iVar6 + 0x40)) {
        *(undefined4 *)(iVar6 + 0x40) = 0x300;
      }
      if (0x380 < *(uint *)(iVar6 + 0x44)) {
        *(undefined4 *)(iVar6 + 0x44) = 0x380;
      }
      if (uVar8 < 1000) {
        iVar5 = 0;
        unaff_r5 = 0;
      }
      else if (uVar8 < _DAT_00005064) {
        func_0x00008574(uVar8 + _DAT_00005030,5);
        unaff_r5 = *(int *)(iVar6 + 0x34);
        iVar5 = extraout_r1;
      }
      else {
        if (uVar8 < 2000) {
          func_0x00008574(uVar8 + _DAT_00005034,5);
          unaff_r5 = *(int *)(iVar6 + 0x38) - *(int *)(iVar6 + 0x34);
          iVar4 = *(int *)(iVar6 + 0x34);
          iVar5 = extraout_r1_00;
        }
        else if (uVar8 < _DAT_00005038) {
          func_0x00008574(uVar8 + _DAT_0000503c,5);
          unaff_r5 = *(int *)(iVar6 + 0x3c) - *(int *)(iVar6 + 0x38);
          iVar4 = *(int *)(iVar6 + 0x38);
          iVar5 = extraout_r1_01;
        }
        else {
          if (uVar8 < _DAT_00005068) {
            func_0x00008574(uVar8 + _DAT_00005040,5);
            unaff_r5 = *(int *)(iVar6 + 0x40) - *(int *)(iVar6 + 0x3c);
            iVar10 = iVar10 + *(int *)(iVar6 + 0x3c);
            iVar5 = extraout_r1_02;
            goto LAB_00004fa6;
          }
          unaff_r5 = *(int *)(iVar6 + 0x44);
          if (_DAT_00005044 <= uVar8) {
            iVar5 = 100;
            goto LAB_00004fa6;
          }
          func_0x00008574(uVar8 + _DAT_00005048,5);
          iVar4 = *(int *)(iVar6 + 0x40);
          unaff_r5 = unaff_r5 - iVar4;
          iVar5 = extraout_r1_03;
        }
        iVar10 = iVar10 + iVar4;
      }
    }
  }
  else {
    iVar5 = 0;
    iStack_20 = 0;
    iStack_28 = 0;
    iStack_24 = 0;
    *(undefined4 *)(iVar6 + 0x2c) = 0xf00;
    iVar9 = 0;
  }
LAB_00004fa6:
  func_0x00008584(iVar5 * unaff_r5,100);
  if (iVar9 == 0) {
    iStack_28 = ((extraout_r1_12 + iVar10) - iStack_24) + iStack_28;
  }
  else {
    iStack_28 = (extraout_r1_12 + iVar10 + *(int *)(iVar6 + 0x48) + (uint)bStack_2b) - iStack_18;
    iStack_20 = iVar7;
  }
  uVar8 = (uint)*pbVar3;
  func_0x00008584(iStack_20 * 0x500,100,iStack_28,uVar8);
  func_0x00008584(uVar8 * extraout_r1_13,100);
  func_0x00008584(uVar8 * pbVar3[1],100);
  func_0x00008574(extraout_r1_15 * 0x500,100);
  uVar8 = extraout_r1_14;
  if (extraout_r1_16 < extraout_r1_14) {
    uVar8 = extraout_r1_16;
  }
                    /* WARNING: Could not recover jumptable at 0x00005014. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)(iStack_28 - uVar8);
  return;
}



// === FUN_000059e8 at 000059e8 (722 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000059e8(int param_1,char param_2)

{
  int iVar1;
  undefined1 uVar2;
  undefined4 uVar3;
  int iVar4;
  undefined1 extraout_r1;
  char cVar5;
  undefined1 extraout_r1_00;
  uint extraout_r1_01;
  uint uVar6;
  undefined4 extraout_r1_02;
  int extraout_r1_03;
  undefined4 extraout_r1_04;
  int extraout_r1_05;
  uint extraout_r1_06;
  int iVar7;
  int iVar8;
  undefined4 uVar9;
  code *UNRECOVERED_JUMPTABLE;
  undefined8 uVar10;
  
  iVar1 = _DAT_00005cdc;
  iVar4 = _DAT_00005cbc;
  if (param_1 != 0) {
    *(undefined1 *)(_DAT_00005cdc + 0x1a) = 0;
    func_0x0000573c(2);
    goto LAB_00005cb2;
  }
  uVar3 = *(undefined4 *)(_DAT_00005cdc + 0x1c);
  cVar5 = *(char *)(_DAT_00005cdc + 0x12);
  iVar7 = _DAT_00005cdc + 200;
  iVar8 = _DAT_00005cdc + 0xcc;
  if (*(char *)(_DAT_00005cdc + 0x1a) == '\x01') {
    if (cVar5 == '\x01') {
      iVar4 = FUN_00006b8c();
      if (iVar4 == 0) goto LAB_00005cb2;
      if ((*_DAT_00005cec & 8) == 0) {
LAB_00005c88:
        FUN_00006b64(*(undefined4 *)(iVar1 + 0x1c),iVar7,4);
        goto LAB_00005cb2;
      }
      *(undefined1 *)(iVar1 + 0x11) = 1;
    }
    else if (cVar5 == '\x02') {
      iVar4 = FUN_00006b8c();
      if (iVar4 == 0) goto LAB_00005cb2;
      iVar7 = iVar8;
      if ((*_DAT_00005cec & 0x10) == 0) goto LAB_00005c88;
    }
  }
  else {
    if (*(char *)(_DAT_00005cdc + 0x1a) != '\x02') {
      if ((*_DAT_00005cec & 8) == 0) {
        *(undefined1 *)(_DAT_00005cdc + 0x12) = 1;
        if (param_2 == '\0') {
          if ((*_DAT_00005ce0 == '\0') && (*_DAT_00005ce4 == '\0')) goto LAB_00005a54;
LAB_00005a4e:
          if (*(char *)(iVar1 + 0x10) != '\0') goto LAB_00005a54;
        }
        else {
          if (*_DAT_00005ce8 != '\0') goto LAB_00005a4e;
LAB_00005a54:
          *(undefined1 *)(iVar1 + 0xf) = 1;
        }
        if (((int)(*_DAT_00005cec << 0x1d) < 0) && (*(char *)(iVar1 + 0xf) == '\0')) {
          FUN_00005ebc();
          goto LAB_00005cb2;
        }
        *(undefined1 *)(iVar1 + 0xf) = 0;
        func_0x0000573c(2);
        FUN_00005ebc();
        uVar9 = 9;
        iVar7 = iVar1 + 0xd0;
        uVar3 = *(undefined4 *)(iVar1 + 0x1c);
        iVar4 = iVar1;
      }
      else {
        if ((*_DAT_00005cec & 0x10) != 0) {
          *(undefined1 *)(_DAT_00005cdc + 0x12) = 0;
          goto LAB_00005cb2;
        }
        *(undefined1 *)(_DAT_00005cdc + 0x12) = 2;
        uVar9 = 0xe;
        iVar7 = iVar1 + 0xdc;
      }
      iVar4 = FUN_00006b9c(uVar3,iVar4,iVar7,uVar9);
      if (iVar4 != 0) {
        *(undefined1 *)(iVar1 + 0x1a) = 2;
      }
      goto LAB_00005cb2;
    }
    if (cVar5 == '\x01') {
      iVar4 = FUN_00006b64(uVar3,iVar7,4);
      if (iVar4 != 0) {
        *(undefined1 *)(iVar1 + 0x1a) = 1;
        *(uint *)(iVar1 + 0x20) = (uint)*(byte *)(iVar1 + 1) + (uint)*(byte *)(iVar1 + 2) * 0x100;
        *(uint *)(iVar1 + 0x24) = (uint)*(byte *)(iVar1 + 5) + (uint)*(byte *)(iVar1 + 6) * 0x100;
        *(int *)(iVar1 + 0x28) =
             (int)((uint)*(byte *)(iVar1 + 7) + (uint)*(byte *)(iVar1 + 8) * 0x100) >> 2;
      }
      goto LAB_00005cb2;
    }
    if (cVar5 == '\x02') {
      iVar7 = FUN_00006b64(uVar3,iVar8,4);
      if (iVar7 != 0) {
        *(undefined1 *)(iVar1 + 0x1a) = 1;
        iVar7 = func_0x00008504(iVar4 + 1,iVar1 + 0x6c,4);
        if (iVar7 == 0) {
          func_0x00008584((uint)*(byte *)(iVar4 + 7) << 2,10);
          uVar6 = extraout_r1_01;
          if (100 < extraout_r1_01) {
            uVar6 = 100;
          }
          *(uint *)(iVar1 + 0x2c) = uVar6;
          *(undefined1 *)(iVar1 + 0x16) = *(undefined1 *)(iVar4 + 8);
        }
        else {
          iVar7 = func_0x00008504(iVar4 + 1,iVar1 + 0x78,4);
          if (iVar7 == 0) {
            func_0x00008574((uint)*(byte *)(iVar4 + 8) * 0x3e,100);
            uVar3 = func_0x00007140(extraout_r1_02);
            func_0x00005f04(uVar3,*_DAT_00005cc0);
            uVar10 = func_0x00007160();
            func_0x00007128((int)uVar10,(int)((ulonglong)uVar10 >> 0x20),_DAT_00005cc4,_DAT_00005cc8
                           );
            uVar2 = func_0x00005f0c();
            *(undefined1 *)(iVar1 + 0x13) = uVar2;
          }
          else {
            iVar7 = func_0x00008504(iVar4 + 1,iVar1 + 0x68,4);
            if (iVar7 == 0) {
              func_0x00008574((uint)*(byte *)(iVar4 + 6) * 9,5);
              *(int *)(iVar1 + 0x30) = extraout_r1_03 + -0x28;
            }
            else {
              iVar7 = func_0x00008504(iVar4 + 1,iVar1 + 0x70,4);
              if (iVar7 == 0) {
                func_0x00008574(((uint)*(byte *)(iVar4 + 0xc) + (uint)*(byte *)(iVar4 + 0xd) * 0x100
                                ) * 5,10);
                *(undefined4 *)(iVar1 + 0x34) = extraout_r1_04;
              }
              else {
                iVar7 = func_0x00008504(iVar4 + 1,iVar1 + 0x74,4);
                if (iVar7 == 0) {
                  func_0x00008584((uint)*(byte *)(iVar4 + 9) * 0x3a,100);
                  *(undefined1 *)(iVar1 + 0x14) = extraout_r1;
                }
                else {
                  iVar7 = func_0x00008504(iVar4 + 1,iVar1 + 0x44,2);
                  if (iVar7 == 0) {
                    func_0x00008574(_DAT_00005ccc *
                                    ((uint)*(byte *)(iVar4 + 0xc) +
                                    (uint)*(byte *)(iVar4 + 0xd) * 0x100),_DAT_00005cd0);
                    *(int *)(iVar1 + 0x38) = extraout_r1_05 + _DAT_00005cd4;
                  }
                  else {
                    iVar7 = func_0x00008504(iVar4 + 1,iVar1 + 0x80,4);
                    if (iVar7 == 0) {
                      *(byte *)(iVar1 + 0x18) = *(byte *)(iVar4 + 1) >> 1;
                    }
                    else {
                      iVar7 = func_0x00008504(iVar4 + 1,iVar1 + 0x7c,4);
                      if (iVar7 == 0) {
                        func_0x00008564((uint)*(byte *)(iVar4 + 7) << 1,7);
                        cVar5 = (char)extraout_r1_06;
                        if (*_DAT_00005cd8 == '\x01') {
                          if ((extraout_r1_06 & 0xff) < 0xd) {
                            cVar5 = '\r';
                          }
                          cVar5 = cVar5 + -0xd;
                        }
                        *(char *)(iVar1 + 0x17) = cVar5;
                        func_0x00008574((uint)*(byte *)(iVar4 + 8) * 9,5);
                        *(undefined1 *)(iVar1 + 0x15) = extraout_r1_00;
                      }
                      else {
                        iVar7 = func_0x00008504(iVar4 + 1,iVar1 + 0x84,4);
                        if ((iVar7 == 0) && (*(char *)(iVar4 + 6) == -0x45)) {
                          *(undefined1 *)(iVar1 + 0x19) = 1;
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
      goto LAB_00005cb2;
    }
  }
  *(undefined1 *)(iVar1 + 0x1a) = 0;
LAB_00005cb2:
                    /* WARNING: Could not recover jumptable at 0x00005cb8. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)();
  return;
}



// === FUN_00006c94 at 00006c94 (706 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00006c94(void)

{
  char *pcVar1;
  char *pcVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  code *UNRECOVERED_JUMPTABLE;
  undefined8 uVar7;
  undefined8 uVar8;
  
  pcVar1 = _DAT_00006f58;
  if (_DAT_00006f58[2] != '\0') {
    pcVar1[0x48] = '\0';
    pcVar1[0x49] = '\0';
    pcVar1[0x4a] = '\0';
    pcVar1[0x4b] = '\0';
    pcVar1[2] = '\0';
  }
  if ((pcVar1[1] != '\0') &&
     (uVar5 = *(uint *)(pcVar1 + 0x48), *(uint *)(pcVar1 + 0x48) = uVar5 + 1, 100 < uVar5)) {
    pcVar1[3] = '\x01';
    pcVar1[1] = '\0';
  }
  if (pcVar1[5] != '\0') {
    pcVar1[0x4c] = '\0';
    pcVar1[0x4d] = '\0';
    pcVar1[0x4e] = '\0';
    pcVar1[0x4f] = '\0';
    pcVar1[5] = '\0';
  }
  uVar5 = _DAT_00006f5c;
  if ((pcVar1[4] != '\0') &&
     (uVar6 = *(uint *)(pcVar1 + 0x4c), *(uint *)(pcVar1 + 0x4c) = uVar6 + 1, uVar5 <= uVar6)) {
    func_0x00007f40();
    pcVar1[4] = '\0';
  }
  if (pcVar1[7] != '\0') {
    pcVar1[0x50] = '\0';
    pcVar1[0x51] = '\0';
    pcVar1[0x52] = '\0';
    pcVar1[0x53] = '\0';
    pcVar1[7] = '\0';
  }
  if ((pcVar1[6] != '\0') &&
     (uVar6 = *(uint *)(pcVar1 + 0x50), *(uint *)(pcVar1 + 0x50) = uVar6 + 1, uVar5 <= uVar6)) {
    func_0x00007f28();
    pcVar1[6] = '\0';
  }
  if (pcVar1[9] != '\0') {
    pcVar1[0x54] = '\0';
    pcVar1[0x55] = '\0';
    pcVar1[0x56] = '\0';
    pcVar1[0x57] = '\0';
    pcVar1[9] = '\0';
  }
  if ((pcVar1[8] != '\0') &&
     (uVar6 = *(uint *)(pcVar1 + 0x54), *(uint *)(pcVar1 + 0x54) = uVar6 + 1, uVar5 <= uVar6)) {
    pcVar1[10] = '\x01';
    pcVar1[8] = '\0';
  }
  if (pcVar1[0xf] != '\0') {
    pcVar1[0x58] = '\0';
    pcVar1[0x59] = '\0';
    pcVar1[0x5a] = '\0';
    pcVar1[0x5b] = '\0';
    pcVar1[0xf] = '\0';
  }
  if ((pcVar1[0xe] != '\0') &&
     (uVar6 = *(uint *)(pcVar1 + 0x58), *(uint *)(pcVar1 + 0x58) = uVar6 + 1, 500 < uVar6)) {
    pcVar1[0x10] = '\x01';
    pcVar1[0xe] = '\0';
  }
  if (pcVar1[0x15] != '\0') {
    pcVar1[0x5c] = '\0';
    pcVar1[0x5d] = '\0';
    pcVar1[0x5e] = '\0';
    pcVar1[0x5f] = '\0';
    pcVar1[0x15] = '\0';
  }
  if ((pcVar1[0x14] != '\0') &&
     (uVar6 = *(uint *)(pcVar1 + 0x5c), *(uint *)(pcVar1 + 0x5c) = uVar6 + 1, 0x96 < uVar6)) {
    pcVar1[0x16] = '\x01';
    pcVar1[0x14] = '\0';
  }
  if (pcVar1[0x18] != '\0') {
    pcVar1[0x60] = '\0';
    pcVar1[0x61] = '\0';
    pcVar1[0x62] = '\0';
    pcVar1[99] = '\0';
    pcVar1[0x18] = '\0';
  }
  if ((pcVar1[0x17] != '\0') &&
     (uVar6 = *(uint *)(pcVar1 + 0x60), *(uint *)(pcVar1 + 0x60) = uVar6 + 1, 0x1f < uVar6)) {
    builtin_strncpy(pcVar1 + 0x19,"\x01\x01\x01\x01",4);
  }
  pcVar2 = _DAT_00006f60;
  if (_DAT_00006f60[1] != '\0') {
    pcVar1[100] = '\0';
    pcVar1[0x65] = '\0';
    pcVar1[0x66] = '\0';
    pcVar1[0x67] = '\0';
    pcVar2[1] = '\0';
  }
  if ((*pcVar2 != '\0') &&
     (uVar6 = *(uint *)(pcVar1 + 100), *(uint *)(pcVar1 + 100) = uVar6 + 1, 400 < uVar6)) {
    pcVar2[2] = '\x01';
    *pcVar2 = '\0';
  }
  if (pcVar1[0x1e] != '\0') {
    pcVar1[0x68] = '\0';
    pcVar1[0x69] = '\0';
    pcVar1[0x6a] = '\0';
    pcVar1[0x6b] = '\0';
    pcVar1[0x1e] = '\0';
  }
  if ((pcVar1[0x1d] != '\0') &&
     (uVar6 = *(uint *)(pcVar1 + 0x68), *(uint *)(pcVar1 + 0x68) = uVar6 + 1, 5 < uVar6)) {
    while ((*_DAT_00006f64 & 4) == 0) {
      *_DAT_00006f9c = 4;
    }
    pcVar1[0x1f] = '\x01';
    pcVar1[0x1d] = '\0';
    pcVar2[0xc] = '\x01';
    pcVar2[0xd] = '\0';
  }
  if (pcVar2[4] != '\0') {
    pcVar1[0x6c] = '\0';
    pcVar1[0x6d] = '\0';
    pcVar1[0x6e] = '\0';
    pcVar1[0x6f] = '\0';
    pcVar2[4] = '\0';
  }
  if ((pcVar2[3] != '\0') &&
     (uVar6 = *(uint *)(pcVar1 + 0x6c), *(uint *)(pcVar1 + 0x6c) = uVar6 + 1, _DAT_00006f68 <= uVar6
     )) {
    pcVar2[5] = '\x01';
    pcVar2[3] = '\0';
  }
  if (pcVar2[7] != '\0') {
    pcVar1[0x70] = '\0';
    pcVar1[0x71] = '\0';
    pcVar1[0x72] = '\0';
    pcVar1[0x73] = '\0';
    pcVar2[7] = '\0';
  }
  if ((pcVar2[6] != '\0') &&
     (uVar6 = *(uint *)(pcVar1 + 0x70), *(uint *)(pcVar1 + 0x70) = uVar6 + 1, _DAT_00006f6c <= uVar6
     )) {
    pcVar2[8] = '\x01';
    pcVar2[6] = '\0';
  }
  if (pcVar2[10] != '\0') {
    pcVar1[0x74] = '\0';
    pcVar1[0x75] = '\0';
    pcVar1[0x76] = '\0';
    pcVar1[0x77] = '\0';
    pcVar2[10] = '\0';
  }
  if ((pcVar2[9] != '\0') &&
     (uVar6 = *(uint *)(pcVar1 + 0x74), *(uint *)(pcVar1 + 0x74) = uVar6 + 1, _DAT_00006f70 <= uVar6
     )) {
    pcVar2[0xb] = '\x01';
    pcVar2[9] = '\0';
  }
  if (pcVar2[0xc] != '\0') {
    pcVar1[0x78] = '\0';
    pcVar1[0x79] = '\0';
    pcVar1[0x7a] = '\0';
    pcVar1[0x7b] = '\0';
    pcVar2[0xc] = '\0';
  }
  uVar6 = *(uint *)(pcVar1 + 0x78);
  *(uint *)(pcVar1 + 0x78) = uVar6 + 1;
  if (uVar5 <= uVar6) {
    pcVar2[0xd] = '\x01';
  }
  if (pcVar1[0xc] != '\0') {
    pcVar1[0x2c] = '\0';
    pcVar1[0x2d] = '\0';
    pcVar1[0x2e] = '\0';
    pcVar1[0x2f] = '\0';
    pcVar1[0xc] = '\0';
  }
  if ((pcVar1[0xb] != '\0') &&
     (uVar5 = *(uint *)(pcVar1 + 0x2c), *(uint *)(pcVar1 + 0x2c) = uVar5 + 1,
     *(uint *)(pcVar1 + 0x24) < uVar5)) {
    pcVar1[0xd] = '\x01';
    pcVar1[0xb] = '\0';
  }
  if (pcVar1[0x12] != '\0') {
    pcVar1[0x7c] = '\0';
    pcVar1[0x7d] = '\0';
    pcVar1[0x7e] = '\0';
    pcVar1[0x7f] = '\0';
    pcVar1[0x12] = '\0';
  }
  if ((pcVar1[0x11] != '\0') &&
     (uVar5 = *(uint *)(pcVar1 + 0x7c), *(uint *)(pcVar1 + 0x7c) = uVar5 + 1,
     *(uint *)(pcVar1 + 0x28) < uVar5)) {
    pcVar1[0x13] = '\x01';
    pcVar1[0x11] = '\0';
  }
  if (pcVar2[0xf] != '\0') {
    pcVar2[0x14] = '\0';
    pcVar2[0x15] = '\0';
    pcVar2[0x16] = '\0';
    pcVar2[0x17] = '\0';
    pcVar2[0xf] = '\0';
  }
  if ((pcVar2[0xe] != '\0') &&
     (uVar5 = *(uint *)(pcVar2 + 0x14), *(uint *)(pcVar2 + 0x14) = uVar5 + 1, _DAT_00006f74 <= uVar5
     )) {
    pcVar2[0x10] = '\x01';
    pcVar2[0xe] = '\0';
  }
  if (*pcVar1 != '\0') {
    pcVar2[0x18] = '\0';
    pcVar2[0x19] = '\0';
    pcVar2[0x1a] = '\0';
    pcVar2[0x1b] = '\0';
    *pcVar1 = '\0';
  }
  uVar5 = *(uint *)(pcVar2 + 0x18);
  *(uint *)(pcVar2 + 0x18) = uVar5 + 1;
  if ((_DAT_00006f78 <= uVar5) && (*_DAT_00006f7c != '\0')) {
    uVar7 = func_0x00007120(*_DAT_00006f80);
    func_0x00007128((int)uVar7,(int)((ulonglong)uVar7 >> 0x20),0,_DAT_00006f84);
    uVar3 = func_0x00007138();
    *(undefined4 *)(pcVar1 + 0x38) = uVar3;
    uVar4 = func_0x00007140(*(undefined4 *)(pcVar1 + 0x34));
    func_0x00007148(uVar4,uVar3);
    uVar4 = func_0x00007150();
    *(undefined4 *)(pcVar1 + 0x34) = uVar4;
    uVar7 = func_0x00007120();
    func_0x00007128((int)uVar7,(int)((ulonglong)uVar7 >> 0x20),_DAT_00006f88,_DAT_00006f8c);
    uVar4 = func_0x00007158();
    *(undefined4 *)(pcVar1 + 0x30) = uVar4;
    uVar7 = func_0x00007160(uVar3);
    uVar7 = func_0x00007128((int)uVar7,(int)((ulonglong)uVar7 >> 0x20),0,_DAT_00006f90);
    uVar8 = func_0x00007160(*(undefined4 *)(pcVar1 + 0x44));
    func_0x00007168((int)uVar8,(int)((ulonglong)uVar8 >> 0x20),(int)uVar7,
                    (int)((ulonglong)uVar7 >> 0x20));
    uVar3 = func_0x00007138();
    *(undefined4 *)(pcVar1 + 0x44) = uVar3;
    uVar7 = func_0x00007120(*_DAT_00006f94);
    func_0x00007128((int)uVar7,(int)((ulonglong)uVar7 >> 0x20),0,_DAT_00006f98);
    uVar3 = func_0x00007138();
    *(undefined4 *)(pcVar1 + 0x3c) = uVar3;
    uVar3 = func_0x00007148(*(undefined4 *)(pcVar1 + 0x40));
    *(undefined4 *)(pcVar1 + 0x40) = uVar3;
    *pcVar1 = '\x01';
  }
                    /* WARNING: Could not recover jumptable at 0x00006f54. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)();
  return;
}



// === FUN_000077b8 at 000077b8 (646 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000077b8(void)

{
  char cVar1;
  undefined1 *puVar2;
  undefined4 *puVar3;
  undefined1 uVar4;
  uint uVar5;
  undefined4 uVar6;
  undefined1 *puVar7;
  int iVar8;
  
  puVar2 = _DAT_00007a40;
  uVar5 = 0;
  do {
    *(undefined4 *)(*(int *)(puVar2 + 0x10) + 0x130) = 0xffffffff;
    uVar5 = uVar5 + 1;
  } while (uVar5 < 10);
  func_0x000073cc();
  func_0x000073dc();
  FUN_000073e4();
  *_DAT_00007a44 = _DAT_00007a48;
  func_0x00200cfc();
  FUN_000074e8();
  FUN_00005f14();
  puVar2[7] = *_DAT_00007a4c;
  FUN_00004384();
  puVar2[1] = 0;
  *puVar2 = 0;
  *_DAT_00007a50 = 0;
  *_DAT_00007a54 = 1;
  *_DAT_00007a5c = 1;
  *_DAT_00007a58 = 0x2000000;
  *_DAT_00007a60 = 0;
  *_DAT_00007a64 = '\0';
  *_DAT_00007a68 = 1;
  puVar3 = _DAT_00007a6c;
  *_DAT_00007a6c = 0x1000000;
  *_DAT_00007a70 = 1;
  *_DAT_00007a74 = '\0';
  *_DAT_00007a78 = 1;
  while (*_DAT_00007a74 == '\0') {
    *puVar3 = 0x1000000;
  }
  uVar4 = func_0x0000760c();
  puVar2[8] = uVar4;
  *_DAT_00007a7c = 0;
  func_0x000047b0(1);
  *_DAT_00007a80 = 1;
  uVar6 = func_0x000073d4();
  puVar7 = _DAT_00007a84;
  *_DAT_00007a84 = (char)uVar6;
  puVar7[1] = (char)((uint)uVar6 >> 8);
  puVar7[2] = (char)((uint)uVar6 >> 0x10);
  puVar7[3] = (char)((uint)uVar6 >> 0x18);
  puVar7 = _DAT_00007a88;
LAB_00007868:
  do {
    *puVar7 = 1;
LAB_000078e4:
    if ((int)(*_DAT_00007af4 << 2) < 0) {
      *_DAT_00007ad4 = _DAT_00007ad8;
    }
    cVar1 = puVar2[8];
    if (cVar1 == '\x01') {
      puVar2[10] = 1;
      *_DAT_00007a60 = 0;
      *_DAT_00007a64 = '\0';
      *_DAT_00007a68 = 1;
      *puVar3 = 0x2000000;
      *puVar3 = 0x1000000;
      if ((*_DAT_00007af4 & 0x10000000) != 0) {
        if (*_DAT_00007aa8 != '\0') {
          *_DAT_00007aa8 = '\0';
        }
        iVar8 = func_0x000074c4();
        if (iVar8 == 0) {
          if (*_DAT_00007aac == '\0') {
LAB_00007992:
            puVar2[8] = 0;
            goto LAB_000078e4;
          }
          if (*_DAT_00007ab0 == '\0') {
            *_DAT_00007abc = 1;
            *_DAT_00007ac0 = '\0';
            *_DAT_00007ac4 = 0;
            *(ushort *)(puVar2 + 0xc) = *_DAT_00007ab8;
            puVar2[8] = 2;
            *_DAT_00007ab4 = 1;
            *_DAT_00007ae8 = _DAT_00007ae0;
            *_DAT_00007af0 = '\0';
            puVar7 = _DAT_00007ae4;
            goto LAB_00007868;
          }
          *_DAT_00007ab4 = 1;
          iVar8 = _DAT_00007adc * (uint)*_DAT_00007ab8;
        }
        else {
          *_DAT_00007ab4 = 1;
          iVar8 = _DAT_00007ac8;
        }
        *_DAT_00007ae8 = iVar8;
        *_DAT_00007af0 = '\0';
        *_DAT_00007ae4 = 1;
        puVar2[8] = 2;
        goto LAB_000078e4;
      }
LAB_00007924:
      FUN_000076cc();
      goto LAB_000078e4;
    }
    if (cVar1 != '\x02') {
      if (cVar1 != '\x03') break;
      *puVar3 = 0x1000000;
      if ((*_DAT_00007af4 & 0x10000000) != 0) goto LAB_00007992;
      if (*_DAT_00007a74 == '\0') goto LAB_00007924;
      goto LAB_000078e2;
    }
    puVar2[10] = 1;
    *_DAT_00007a60 = 0;
    *_DAT_00007a64 = '\0';
    *_DAT_00007a68 = 1;
    *puVar3 = 0x2000000;
    *_DAT_00007a58 = 0x1000000;
    iVar8 = func_0x000074c4();
    if (iVar8 != 0) {
      if (*_DAT_00007af0 != '\0') goto LAB_00007a04;
      FUN_000076cc();
      goto LAB_000078e4;
    }
    if ((uint)*(ushort *)(puVar2 + 0xc) < *_DAT_00007aec) {
      *_DAT_00007abc = 1;
      *_DAT_00007ac0 = '\0';
      *_DAT_00007ac4 = 0;
    }
    else {
      *_DAT_00007ac4 = 1;
    }
    if (((*_DAT_00007af0 == '\0') &&
        (((*_DAT_00007ab0 != '\0' || (*_DAT_00007ac0 == '\0')) && (*_DAT_00007acc == 0)))) &&
       (*_DAT_00007ad0 != 0)) goto LAB_00007924;
LAB_00007a04:
    *puVar3 = 0x1000000;
    puVar2[8] = 3;
    *_DAT_00007a70 = 1;
    *_DAT_00007a74 = '\0';
    puVar7 = _DAT_00007a78;
  } while( true );
  *_DAT_00007a8c = 0x7800;
  *_DAT_00007a90 = 0;
  *_DAT_00007a98 = 0x7800;
  uVar6 = _DAT_00007a94;
  *_DAT_00007a9c = _DAT_00007a94;
  *_DAT_00007aa0 = uVar6;
  *puVar3 = 0x20;
  *puVar3 = 0x40;
  *puVar3 = 1;
  *puVar3 = 0x8000;
  *_DAT_00007a60 = 1;
  if (*_DAT_00007a64 != '\0') {
    *_DAT_00007a58 = 0x2000000;
    *_DAT_00007a60 = 0;
    *_DAT_00007a64 = '\0';
    *_DAT_00007a68 = 1;
    puVar2[10] = 0;
  }
  *puVar3 = 0x1000000;
  if ((*_DAT_00007af4 & 0x10000000) == 0) {
    FUN_000074e8();
    puVar2[1] = 0;
    *puVar2 = 0;
    *_DAT_00007a50 = 0;
    *_DAT_00007a54 = 1;
    *_DAT_00007a5c = 1;
    *_DAT_00007a7c = 0;
    func_0x000047b0(1);
    *_DAT_00007aa4 = 0;
LAB_000078e2:
    puVar2[8] = 1;
  }
  goto LAB_000078e4;
}



// === FUN_0000575c at 0000575c (622 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0000575c(void)

{
  char *pcVar1;
  int iVar2;
  byte bVar3;
  int iVar4;
  code *UNRECOVERED_JUMPTABLE;
  
  func_0x0000573c(1);
  func_0x0000573c(2);
  bVar3 = 0;
  do {
    bVar3 = bVar3 + 1;
  } while (bVar3 < 100);
  *_DAT_000059cc = 1;
  pcVar1 = _DAT_000059d0;
  *_DAT_000059d0 = '\0';
  *_DAT_000059d4 = 1;
  iVar2 = _DAT_000059d8;
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 0x46,1);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  bVar3 = 0;
  do {
    bVar3 = bVar3 + 1;
  } while (bVar3 < 100);
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 0x5f,3);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  do {
    iVar4 = FUN_00006b9c(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 0xec,iVar2 + 0x65,3);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 0xbc,5);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 0x50,3);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 0x53,3);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 0xac,6);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 0xb4,6);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 0x88,4);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 0x8c,4);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 0x94,6);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 0x9c,6);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 0xa4,6);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 0x90,4);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 0x56,3);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 0x47,3);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),_DAT_000059dc,9);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 0x59,3);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 0x4a,3);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 0x4d,3);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 0x5c,3);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 200,4);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 0xc4,4);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 0x62,3);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  if (*pcVar1 != '\0') {
    *_DAT_000059e0 = _DAT_000059e4;
  }
  *(undefined1 *)(iVar2 + 0x11) = 0;
  FUN_000059e8(1,0);
  FUN_00005cf0(1,0);
                    /* WARNING: Could not recover jumptable at 0x000059c8. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)();
  return;
}



// === FUN_00004384 at 00004384 (530 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00004384(void)

{
  byte bVar1;
  byte *pbVar2;
  undefined1 *puVar3;
  int iVar4;
  undefined1 uVar5;
  undefined4 uVar6;
  undefined4 extraout_r1;
  undefined4 extraout_r1_00;
  undefined4 extraout_r1_01;
  undefined4 extraout_r1_02;
  undefined4 extraout_r1_03;
  undefined4 extraout_r1_04;
  byte *pbVar7;
  undefined1 uVar8;
  code *UNRECOVERED_JUMPTABLE;
  
  pbVar2 = _DAT_00004638;
  *_DAT_00004638 = 0xb;
  pbVar2[4] = 0xfa;
  pbVar2[5] = 0;
  pbVar2[6] = 0;
  pbVar2[7] = 0;
  pbVar2[8] = 0x1e;
  pbVar2[10] = 100;
  pbVar2[0xb] = 10;
  pbVar2[9] = 0x23;
  pbVar2[0x10] = 8;
  pbVar2[0x11] = 7;
  pbVar2[0x12] = 0;
  pbVar2[0x13] = 0;
  uVar8 = 0;
  pbVar2[0xc] = 0;
  pbVar2[0xe] = 0x32;
  pbVar2[0xd] = 5;
  *(undefined4 *)(pbVar2 + 0x14) = _DAT_00004598;
  pbVar2[0x30] = 0x14;
  pbVar2[0x31] = 100;
  pbVar2[0x32] = 0x14;
  pbVar2[0x33] = 0x1e;
  pbVar2[0x34] = 0x96;
  pbVar2[0x35] = 0;
  pbVar2[0x36] = 0;
  pbVar2[0x37] = 0;
  pbVar2[0x38] = 0xb4;
  pbVar2[0x39] = 0;
  pbVar2[0x3a] = 0;
  pbVar2[0x3b] = 0;
  pbVar2[0x3c] = 0xd2;
  pbVar2[0x3d] = 0;
  pbVar2[0x3e] = 0;
  pbVar2[0x3f] = 0;
  pbVar2[0x40] = 0xe6;
  pbVar2[0x41] = 0;
  pbVar2[0x42] = 0;
  pbVar2[0x43] = 0;
  pbVar2[0x18] = 0x65;
  pbVar2[0x19] = 0x67;
  pbVar2[0x1a] = 0x69;
  pbVar2[0x1b] = 0x6b;
  pbVar2[0x1c] = 0x6e;
  pbVar2[0x1d] = 0x71;
  pbVar2[0x1e] = 0x74;
  pbVar2[0x1f] = 0x77;
  pbVar2[0x20] = 0x7a;
  pbVar2[0x21] = 0x7d;
  pbVar2[0x22] = 0x80;
  pbVar2[0x23] = 0x83;
  pbVar2[0x24] = 0x86;
  pbVar2[0x25] = 0x89;
  pbVar2[0x26] = 0x8c;
  pbVar2[0x27] = 0x8f;
  pbVar2[0x28] = 0x92;
  pbVar2[0x29] = 0x95;
  pbVar2[0x2a] = 0x96;
  pbVar2[0x2b] = 0x96;
  pbVar2[0x2c] = 0x96;
  pbVar2[0x2d] = 0x96;
  pbVar2[0x2e] = 0x96;
  pbVar2[0x2f] = 0x96;
  iVar4 = _DAT_0000463c;
  *(undefined1 *)(_DAT_0000463c + 0xf) = 10;
  pbVar7 = pbVar2;
  uVar5 = func_0x00008584(100,*pbVar2 - 1);
  *(undefined1 *)(iVar4 + 0x10) = uVar5;
  *_DAT_0000459c = *pbVar7;
  puVar3 = _DAT_000045a0;
  uVar6 = *(undefined4 *)(pbVar7 + 4);
  *_DAT_000045a0 = (char)uVar6;
  puVar3[1] = (char)((uint)uVar6 >> 8);
  puVar3 = _DAT_000045a4;
  uVar6 = *(undefined4 *)(pbVar2 + 0x34);
  *_DAT_000045a4 = (char)uVar6;
  puVar3[1] = (char)((uint)uVar6 >> 8);
  puVar3 = _DAT_000045a8;
  uVar6 = *(undefined4 *)(pbVar2 + 0x38);
  *_DAT_000045a8 = (char)uVar6;
  puVar3[1] = (char)((uint)uVar6 >> 8);
  puVar3 = _DAT_000045ac;
  uVar6 = *(undefined4 *)(pbVar2 + 0x3c);
  *_DAT_000045ac = (char)uVar6;
  puVar3[1] = (char)((uint)uVar6 >> 8);
  puVar3 = _DAT_000045b0;
  uVar6 = *(undefined4 *)(pbVar2 + 0x40);
  *_DAT_000045b0 = (char)uVar6;
  puVar3[1] = (char)((uint)uVar6 >> 8);
  *_DAT_00004640 = pbVar7[8];
  *_DAT_000045b4 = pbVar7[10];
  *_DAT_000045b8 = pbVar7[0xb];
  *_DAT_00004644 = 0x14;
  *_DAT_000045bc = pbVar2[0x31];
  *_DAT_00004648 = 0x14;
  *_DAT_0000464c = pbVar2[0x33];
  *_DAT_000045c0 = pbVar7[9];
  puVar3 = _DAT_000045c4;
  uVar6 = *(undefined4 *)(pbVar7 + 0x10);
  *_DAT_000045c4 = (char)uVar6;
  puVar3[1] = (char)((uint)uVar6 >> 8);
  puVar3 = _DAT_000045c8;
  uVar6 = *(undefined4 *)(pbVar7 + 0x14);
  *_DAT_000045c8 = (char)uVar6;
  puVar3[1] = (char)((uint)uVar6 >> 8);
  *_DAT_000045cc = uVar8;
  *_DAT_000045d0 = pbVar7[0xe];
  *_DAT_000045d4 = pbVar7[0xd];
  *_DAT_000045d8 = pbVar7[0x18];
  *_DAT_000045dc = pbVar7[0x19];
  *_DAT_000045e0 = pbVar7[0x1a];
  *_DAT_000045e4 = pbVar7[0x1b];
  *_DAT_000045e8 = pbVar7[0x1c];
  *_DAT_000045ec = pbVar7[0x1d];
  *_DAT_000045f0 = pbVar7[0x1e];
  *_DAT_000045f4 = pbVar7[0x1f];
  *_DAT_000045f8 = pbVar2[0x20];
  *_DAT_000045fc = pbVar2[0x21];
  *_DAT_00004600 = pbVar2[0x22];
  *_DAT_00004604 = pbVar2[0x23];
  *_DAT_00004608 = pbVar2[0x24];
  *_DAT_0000460c = pbVar2[0x25];
  *_DAT_00004610 = pbVar2[0x26];
  *_DAT_00004614 = pbVar2[0x27];
  *_DAT_00004618 = pbVar2[0x28];
  *_DAT_0000461c = pbVar2[0x29];
  bVar1 = pbVar2[0x2a];
  *_DAT_00004620 = bVar1;
  *_DAT_00004624 = bVar1;
  *_DAT_00004628 = bVar1;
  *_DAT_0000462c = bVar1;
  *_DAT_00004630 = bVar1;
  *_DAT_00004634 = bVar1;
  func_0x00008574((uint)bVar1 << 7,10);
  *(undefined4 *)(iVar4 + 0x34) = extraout_r1;
  func_0x00008574(*(int *)(pbVar2 + 0x38) << 7,10);
  *(undefined4 *)(iVar4 + 0x38) = extraout_r1_00;
  func_0x00008574(*(int *)(pbVar2 + 0x3c) << 7,10);
  *(undefined4 *)(iVar4 + 0x3c) = extraout_r1_01;
  func_0x00008574(*(int *)(pbVar2 + 0x40) << 7,10);
  *(undefined4 *)(iVar4 + 0x40) = extraout_r1_02;
  func_0x00008574(*(int *)(pbVar7 + 4) << 7,10);
  *(undefined4 *)(iVar4 + 0x44) = extraout_r1_03;
  func_0x00008584(0xa00,10);
  *(undefined4 *)(iVar4 + 0x48) = extraout_r1_04;
  *(undefined1 *)(iVar4 + 1) = uVar8;
  *(undefined1 *)(iVar4 + 2) = 1;
                    /* WARNING: Could not recover jumptable at 0x00004594. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)();
  return;
}



// === FUN_00004b38 at 00004b38 (290 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00004b38(undefined4 param_1,int param_2,uint param_3,int param_4,uint param_5,byte param_6,
                 byte param_7)

{
  uint *puVar1;
  int iVar2;
  undefined1 uVar3;
  uint uVar4;
  int extraout_r1;
  int extraout_r1_00;
  uint extraout_r1_01;
  int extraout_r1_02;
  uint extraout_r1_03;
  uint extraout_r1_04;
  uint extraout_r1_05;
  int extraout_r1_06;
  int iVar5;
  undefined4 uVar6;
  undefined4 *puVar7;
  code *UNRECOVERED_JUMPTABLE;
  
  iVar2 = _DAT_00004d24;
  puVar1 = _DAT_00004d20;
  if ((int)((uint)*(byte *)(_DAT_00004d24 + 0xf) * 2 + (uint)*(byte *)(_DAT_00004d24 + 0x10)) <
      param_2) {
    if ((param_5 < _DAT_00004d0c) || (*_DAT_00004d20 <= param_5)) {
      iVar5 = 0;
    }
    else {
      func_0x00008574(param_5 + _DAT_00004d10,5);
      func_0x00008574(param_4 * extraout_r1,100);
      iVar5 = extraout_r1_00 + 100;
    }
    switch(*(undefined4 *)(iVar2 + 0x28)) {
    case 0:
      uVar4 = (uint)(byte)puVar1[1];
      break;
    case 1:
      uVar4 = (uint)*(byte *)((int)puVar1 + 5);
      break;
    case 2:
      uVar4 = (uint)*(byte *)((int)puVar1 + 6);
      break;
    case 3:
      uVar4 = (uint)*(byte *)((int)puVar1 + 7);
      break;
    case 4:
      uVar4 = (uint)(byte)puVar1[2];
      break;
    case 5:
      uVar4 = (uint)*(byte *)((int)puVar1 + 9);
      break;
    case 6:
      uVar4 = (uint)*(byte *)((int)puVar1 + 10);
      break;
    case 7:
      uVar4 = (uint)*(byte *)((int)puVar1 + 0xb);
      break;
    case 8:
      uVar4 = (uint)(byte)puVar1[3];
      break;
    case 9:
      uVar4 = (uint)*(byte *)((int)puVar1 + 0xd);
      break;
    case 10:
      uVar4 = (uint)*(byte *)((int)puVar1 + 0xe);
      break;
    case 0xb:
      uVar4 = (uint)*(byte *)((int)puVar1 + 0xf);
      break;
    case 0xc:
      uVar4 = (uint)(byte)puVar1[4];
      break;
    case 0xd:
      uVar4 = (uint)*(byte *)((int)puVar1 + 0x11);
      break;
    case 0xe:
      uVar4 = (uint)*(byte *)((int)puVar1 + 0x12);
      break;
    case 0xf:
      uVar4 = (uint)*(byte *)((int)puVar1 + 0x13);
      break;
    case 0x10:
      uVar4 = (uint)(byte)puVar1[5];
      break;
    case 0x11:
    case 0x12:
      uVar4 = (uint)*(byte *)((int)puVar1 + 0x15);
      break;
    case 0x13:
    case 0x14:
      uVar4 = (uint)*(byte *)((int)puVar1 + 0x16);
      break;
    case 0x15:
    case 0x16:
      uVar4 = (uint)*(byte *)((int)puVar1 + 0x17);
      break;
    case 0x17:
    case 0x18:
      uVar4 = (uint)(byte)puVar1[6];
      break;
    case 0x19:
    case 0x1a:
      uVar4 = (uint)*(byte *)((int)puVar1 + 0x19);
      break;
    case 0x1b:
    case 0x1c:
      uVar4 = (uint)*(byte *)((int)puVar1 + 0x1a);
      break;
    default:
      uVar4 = (uint)*(byte *)((int)puVar1 + 0x1b);
    }
    func_0x00008574(param_3 * uVar4,100,iVar5);
    uVar4 = extraout_r1_01;
    if (param_3 < extraout_r1_01) {
      func_0x00008574(iVar5 * extraout_r1_01,100);
      uVar4 = extraout_r1_01 + extraout_r1_02;
    }
  }
  else {
    if ((int)((uint)*(byte *)(_DAT_00004d24 + 0xf) + (uint)*(byte *)(_DAT_00004d24 + 0x10)) <
        param_2) {
      switch(*(undefined4 *)(_DAT_00004d24 + 0x28)) {
      case 0:
        uVar4 = (uint)(byte)_DAT_00004d20[1];
        break;
      case 1:
        uVar4 = (uint)*(byte *)((int)_DAT_00004d20 + 5);
        break;
      case 2:
        uVar4 = (uint)*(byte *)((int)_DAT_00004d20 + 6);
        break;
      case 3:
        uVar4 = (uint)*(byte *)((int)_DAT_00004d20 + 7);
        break;
      case 4:
        uVar4 = (uint)(byte)_DAT_00004d20[2];
        break;
      case 5:
        uVar4 = (uint)*(byte *)((int)_DAT_00004d20 + 9);
        break;
      case 6:
        uVar4 = (uint)*(byte *)((int)_DAT_00004d20 + 10);
        break;
      case 7:
        uVar4 = (uint)*(byte *)((int)_DAT_00004d20 + 0xb);
        break;
      case 8:
        uVar4 = (uint)(byte)_DAT_00004d20[3];
        break;
      case 9:
        uVar4 = (uint)*(byte *)((int)_DAT_00004d20 + 0xd);
        break;
      default:
        uVar4 = (uint)*(byte *)((int)_DAT_00004d20 + 0xe);
      }
      func_0x00008574(param_3 * uVar4,100);
      uVar4 = extraout_r1_03;
      if (extraout_r1_03 <= param_3) goto LAB_00004c8e;
    }
    else if (param_2 != 0) {
      func_0x00008574(param_3 * *_DAT_00004d14,100);
      uVar4 = extraout_r1_04;
      goto LAB_00004c8e;
    }
    uVar4 = param_3;
  }
LAB_00004c8e:
  iVar5 = func_0x000047b0(0);
  if (iVar5 == 0) {
    uVar6 = *_DAT_00004d28;
    puVar7 = _DAT_00004d2c;
    if (((byte)puVar1[1] < 100) && (*(char *)(iVar2 + 6) != '\0')) {
      func_0x00008574(param_3 * (byte)puVar1[1],100);
      uVar3 = 1;
      uVar4 = extraout_r1_05;
    }
    else {
      uVar3 = 0;
      uVar4 = param_3;
    }
    *puVar7 = uVar6;
  }
  else {
    uVar3 = 0;
  }
  *(undefined1 *)(iVar2 + 10) = uVar3;
  if (((*_DAT_00004d30 < _DAT_00004d34) && (_DAT_00004d18 <= *_DAT_00004d30)) && (uVar4 < param_3))
  {
    func_0x00008574((int)*(char *)(_DAT_00004d1c + (uint)param_6 * 0x14 + (uint)param_7) *
                    (param_3 - uVar4),100);
    uVar4 = uVar4 + extraout_r1_06;
  }
  if (0xfff < (int)uVar4) {
    uVar4 = 0xfff;
  }
                    /* WARNING: Could not recover jumptable at 0x00004d08. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)(uVar4);
  return;
}



// === FUN_00005cf0 at 00005cf0 (250 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00005cf0(int param_1,int param_2)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  undefined4 uVar7;
  code *UNRECOVERED_JUMPTABLE;
  
  iVar3 = _DAT_00005df0;
  if (param_1 == 0) {
    if (param_2 == 0) {
      if (*_DAT_00005df4 == '\0') {
        cVar1 = *_DAT_00005df8;
        goto joined_r0x00005d56;
      }
    }
    else {
      cVar1 = *_DAT_00005dfc;
joined_r0x00005d56:
      if (cVar1 == '\0') {
        *(undefined1 *)(_DAT_00005df0 + 0x1b) = 0;
        *(undefined1 *)(iVar3 + 0x11) = 0;
        goto LAB_00005d00;
      }
    }
    iVar6 = _DAT_00005df0 + 0xc4;
    cVar1 = *(char *)(_DAT_00005df0 + 0x1b);
    if (cVar1 == '\0') {
      if (*(char *)(_DAT_00005df0 + 0x11) == '\0') {
        *(undefined1 *)(_DAT_00005df0 + 0x10) = 1;
      }
      else {
        iVar6 = FUN_00006b64(*(undefined4 *)(_DAT_00005df0 + 0x1c),iVar6,4);
        if (iVar6 != 0) {
          *(undefined1 *)(iVar3 + 0x1b) = 2;
          *(undefined2 *)(iVar3 + 0x10) = 0;
        }
      }
    }
    else if (cVar1 == '\x01') {
      if (*(char *)(_DAT_00005df0 + 0x11) != '\0') {
        if ((*_DAT_00005e00 & 4) == 0) {
          FUN_00006b64(*(undefined4 *)(_DAT_00005df0 + 0x1c),iVar6,4);
        }
        *(undefined1 *)(iVar3 + 0x1b) = 2;
        *(undefined1 *)(iVar3 + 0x11) = 0;
      }
    }
    else if (cVar1 == '\x02') {
      iVar4 = FUN_00006b48();
      iVar2 = _DAT_00005dec;
      if (iVar4 != 0) {
        uVar5 = *(undefined4 *)(iVar3 + 0x1c);
        if ((*_DAT_00005e00 & 4) == 0) {
          FUN_00006b64(uVar5,iVar6,4);
        }
        else {
          uVar7 = *(undefined4 *)(iVar3 + 0x3c);
          *(char *)(_DAT_00005dec + 1) = (char)uVar7;
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
    *(undefined1 *)(_DAT_00005df0 + 0x1b) = 0;
LAB_00005d00:
    *(undefined1 *)(iVar3 + 0x10) = 1;
  }
                    /* WARNING: Could not recover jumptable at 0x00005de8. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)();
  return;
}



// === FUN_00004214 at 00004214 (238 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00004214(void)

{
  char *pcVar1;
  byte *pbVar2;
  undefined4 uVar3;
  int iVar4;
  code *UNRECOVERED_JUMPTABLE;
  
  pbVar2 = _DAT_00004380;
  iVar4 = *_DAT_00004304;
  if (iVar4 << 0x1c < 0) {
    *(bool *)_DAT_0000430c = 0x2a3 < *_DAT_00004308;
    *pbVar2 = *pbVar2 & 0xf7;
  }
  if (iVar4 << 0x1b < 0) {
    uVar3 = func_0x00007398(*_DAT_00004310);
    pcVar1 = _DAT_00004314;
    if (*_DAT_00004314 != '\0') {
      uVar3 = func_0x000041f0(pbVar2 + 0x94,uVar3);
      *(undefined4 *)(pbVar2 + 8) = uVar3;
      *pcVar1 = '\0';
    }
    *pbVar2 = *pbVar2 & 0xef;
  }
  if (iVar4 << 0x1a < 0) {
    uVar3 = func_0x00007380(*_DAT_00004318);
    pcVar1 = _DAT_0000431c;
    if (*_DAT_0000431c != '\0') {
      uVar3 = func_0x000041f0(pbVar2 + 0x14,uVar3);
      *(undefined4 *)(pbVar2 + 4) = uVar3;
      *pcVar1 = '\0';
    }
    *pbVar2 = *pbVar2 & 0xdf;
  }
  if (iVar4 << 0x19 < 0) {
    uVar3 = func_0x000073bc(*_DAT_00004320);
    pcVar1 = _DAT_00004324;
    if (*_DAT_00004324 != '\0') {
      uVar3 = func_0x000041f0(pbVar2 + 0x194,uVar3);
      *(undefined4 *)(pbVar2 + 0x10) = uVar3;
      *pcVar1 = '\0';
    }
    *pbVar2 = *pbVar2 & 0xbf;
  }
  if (iVar4 << 0x18 < 0) {
    uVar3 = func_0x00007364(*_DAT_00004328);
    pcVar1 = _DAT_0000432c;
    if (*_DAT_0000432c != '\0') {
      uVar3 = func_0x000041f0(pbVar2 + 0x114,uVar3);
      *(undefined4 *)(pbVar2 + 0xc) = uVar3;
      *pcVar1 = '\0';
    }
    *pbVar2 = *pbVar2 & 0x7f;
  }
  if (*pbVar2 == 0) {
    *pbVar2 = 0xf8;
    *_DAT_0000437c = 2;
  }
                    /* WARNING: Could not recover jumptable at 0x00004300. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)();
  return;
}



// === FUN_00007d80 at 00007d80 (228 bytes) ===

void FUN_00007d80(undefined1 *param_1,uint param_2,undefined1 *param_3,char *param_4)

{
  undefined1 uVar1;
  byte bVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  byte bVar6;
  char cVar7;
  code *UNRECOVERED_JUMPTABLE;
  undefined1 *puStack_40;
  undefined1 *puStack_3c;
  undefined1 auStack_30 [16];
  uint uStack_20;
  undefined1 *puStack_1c;
  char *pcStack_18;
  
  pcStack_18 = param_4;
  puStack_1c = param_3;
  uStack_20 = param_2;
  uVar5 = 0;
  cVar7 = *param_4;
  puStack_40 = param_3;
  bVar6 = 0;
  while ((cVar7 != '\0' && (bVar6 < 0xe))) {
    bVar2 = bVar6 + 1;
    cVar7 = cVar7 + -1;
    uVar1 = *puStack_40;
    if (((char)uStack_20 == '\x04') || ((uStack_20 & 0xff) == 2)) {
      *param_1 = uVar1;
      puStack_40 = puStack_40 + 1;
      param_1 = param_1 + 1;
      bVar6 = bVar2;
    }
    else {
      puStack_40 = puStack_40 + 1;
      puStack_3c = (undefined1 *)FUN_00007c68(uVar1);
      if ((puStack_3c == (undefined1 *)0x0) ||
         (uVar3 = FUN_00007bf8(*puStack_3c,uVar1), 0xe < (bVar6 + uVar3 + 1 & 0xffff))) {
        auStack_30[uVar5] = uVar1;
        uVar5 = uVar5 + 1 & 0xff;
      }
      else {
        *param_1 = uVar1;
        param_1 = param_1 + 1;
        uVar4 = 0;
        bVar6 = bVar2;
        if (uVar3 != 0) {
          for (; bVar6 = bVar2, uVar4 < uVar3; uVar4 = uVar4 + 1 & 0xff) {
            *param_1 = *puStack_3c;
            puStack_3c = puStack_3c + 1;
            param_1 = param_1 + 1;
            bVar2 = bVar2 + 1;
          }
        }
      }
    }
  }
  uVar3 = 0;
  if (uVar5 != 0) {
    for (; uVar3 < uVar5; uVar3 = uVar3 + 1 & 0xff) {
      puStack_1c[uVar3] = auStack_30[uVar3];
    }
  }
  *pcStack_18 = (char)uVar5;
                    /* WARNING: Could not recover jumptable at 0x00007e62. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)(bVar6);
  return;
}



// === FUN_000076cc at 000076cc (218 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000076cc(void)

{
  char cVar1;
  int iVar2;
  char *pcVar3;
  undefined1 *puVar4;
  undefined1 *puVar5;
  undefined1 uVar6;
  undefined4 uVar7;
  int iVar8;
  code *UNRECOVERED_JUMPTABLE;
  
  FUN_00004214();
  iVar2 = _DAT_000077a8;
  FUN_000059e8(0,*(undefined1 *)(_DAT_000077a8 + 7));
  FUN_0000601c();
  uVar7 = FUN_000050f0();
  *(char *)(iVar2 + 7) = (char)uVar7;
  FUN_00005cf0(0,uVar7);
  puVar5 = _DAT_000077b4;
  puVar4 = _DAT_000077b0;
  pcVar3 = _DAT_000077ac;
  if (*_DAT_000077ac != '\0') {
    cVar1 = *(char *)(iVar2 + 0xb);
    if (cVar1 == '\0') {
      iVar8 = FUN_00007efc(iVar2 + 0x18,*(undefined1 *)(iVar2 + 2));
      if (iVar8 == 0) goto LAB_00007796;
      *pcVar3 = '\0';
      uVar6 = 1;
      *puVar5 = 1;
      *puVar4 = 1;
    }
    else if (cVar1 == '\x01') {
      iVar8 = FUN_00007efc(iVar2 + 0x20,*(undefined1 *)(iVar2 + 3));
      if (iVar8 == 0) goto LAB_00007796;
      *pcVar3 = '\0';
      *puVar5 = 1;
      *puVar4 = 1;
      uVar6 = 2;
    }
    else if (cVar1 == '\x02') {
      iVar8 = FUN_00007efc(iVar2 + 0x28,*(undefined1 *)(iVar2 + 4));
      if (iVar8 == 0) goto LAB_00007796;
      *pcVar3 = '\0';
      *puVar5 = 1;
      *puVar4 = 1;
      uVar6 = 3;
    }
    else if (cVar1 == '\x03') {
      iVar8 = FUN_00007efc(iVar2 + 0x30,*(undefined1 *)(iVar2 + 5));
      if (iVar8 == 0) goto LAB_00007796;
      *pcVar3 = '\0';
      *puVar5 = 1;
      *puVar4 = 1;
      uVar6 = 4;
    }
    else {
      iVar8 = FUN_00007efc(iVar2 + 0x38,*(undefined1 *)(iVar2 + 6));
      if (iVar8 == 0) goto LAB_00007796;
      *pcVar3 = '\0';
      *puVar5 = 1;
      *puVar4 = 1;
      uVar6 = 0;
    }
    *(undefined1 *)(iVar2 + 0xb) = uVar6;
  }
LAB_00007796:
  if (*(char *)(iVar2 + 10) != '\0') {
    FUN_000081a8();
  }
                    /* WARNING: Could not recover jumptable at 0x000077a4. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)();
  return;
}



// === FUN_000046d0 at 000046d0 (192 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000046d0(undefined4 param_1,uint param_2)

{
  char *pcVar1;
  char cVar2;
  byte bVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  uint uVar6;
  byte bVar7;
  code *UNRECOVERED_JUMPTABLE;
  undefined8 uVar8;
  byte abStack_24 [8];
  undefined4 uStack_1c;
  uint uStack_18;
  
  pcVar1 = _DAT_00004790;
  bVar7 = 100;
  uStack_1c = param_1;
  uStack_18 = param_2;
  if (param_2 == 0) {
    *_DAT_00004790 = -0xe;
  }
  else {
    uVar6 = 0;
    if (*(char *)(_DAT_00004798 + (uint)*_DAT_00004794 * 0x1c) != '\0') {
      for (; uVar6 < *(byte *)(_DAT_00004798 + (uint)*_DAT_00004794 * 0x1c);
          uVar6 = uVar6 + 1 & 0xff) {
        uVar4 = func_0x00005f04(*(undefined4 *)
                                 (_DAT_00004798 + uVar6 * 4 + (uint)*_DAT_00004794 * 0x1c + 4),
                                *(undefined4 *)(_DAT_00004798 + (uint)*_DAT_0000479c * 4 + 0x54));
        uVar5 = func_0x00007140(uStack_18 & 0xff);
        uVar4 = func_0x00005f04(uVar5,uVar4);
        uVar4 = func_0x00005f04(uVar4,_DAT_000047a0);
        uVar5 = func_0x00007140(uStack_1c);
        uVar5 = func_0x00005f04(uVar5,*_DAT_000047a4);
        uVar4 = func_0x000056fc(uVar5,uVar4);
        uVar4 = func_0x00007148(uVar4,_DAT_000047a8);
        func_0x00005f04(uVar4,_DAT_000047ac);
        uVar8 = func_0x00007160();
        bVar3 = func_0x00005f0c((int)uVar8,(uint)((ulonglong)uVar8 >> 0x20) & 0x7fffffff);
        abStack_24[uVar6] = bVar3;
        cVar2 = *pcVar1;
        bVar3 = abStack_24[uVar6];
        if (bVar3 < bVar7) {
          bVar7 = bVar3;
          if (uVar6 < 4) {
            cVar2 = (char)(uVar6 + 1);
          }
          else {
            cVar2 = (char)uVar6 + '\x02';
          }
        }
        *pcVar1 = cVar2;
      }
    }
  }
                    /* WARNING: Could not recover jumptable at 0x0000478e. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)(bVar7);
  return;
}



// === FUN_00007cc4 at 00007cc4 (186 bytes) ===

void FUN_00007cc4(undefined1 *param_1,byte param_2,char param_3,undefined1 *param_4,char *param_5)

{
  undefined1 uVar1;
  char cVar2;
  undefined4 uVar3;
  int iVar4;
  undefined1 *puVar5;
  byte bVar6;
  char unaff_r7;
  code *UNRECOVERED_JUMPTABLE;
  char cStack_28;
  
  cStack_28 = '\0';
  iVar4 = 1;
  if (0xe < param_2) {
    param_2 = 0xe;
  }
  bVar6 = 0;
  puVar5 = param_1;
  cVar2 = '\0';
  if (param_2 != 0) {
    for (; cStack_28 = cVar2, bVar6 < param_2; bVar6 = bVar6 + 1) {
      uVar1 = *puVar5;
      if ((param_3 == '\x04') || (param_3 == '\x02')) {
        *param_4 = uVar1;
LAB_00007d2e:
        param_4 = param_4 + 1;
        cStack_28 = cStack_28 + '\x01';
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
      cVar2 = cStack_28;
    }
  }
  *param_5 = cStack_28;
  if (unaff_r7 == '\0') {
    uVar3 = 1;
  }
  else {
    uVar3 = 2;
  }
                    /* WARNING: Could not recover jumptable at 0x00007d7c. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)(uVar3);
  return;
}



// === FUN_000074e8 at 000074e8 (176 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000074e8(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  uint uVar3;
  undefined4 *puVar4;
  int iVar5;
  code *UNRECOVERED_JUMPTABLE;
  
  iVar5 = _DAT_000077a8;
  *(undefined4 *)(*(int *)(_DAT_000077a8 + 0x10) + 0x124) = 0xffffffff;
  *_DAT_00007598 = 0xffffffff;
  *_DAT_0000759c = 4;
  puVar4 = _DAT_000075ec;
  uVar1 = _DAT_000075a0;
  *_DAT_000075ec = _DAT_000075a0;
  *_DAT_000075f0 = uVar1;
  uVar2 = _DAT_000075a4;
  *_DAT_000075a8 = _DAT_000075a4;
  *puVar4 = uVar2;
  *_DAT_000075f4 = uVar1;
  *_DAT_000075ac = uVar2;
  *_DAT_000075b0 = uVar1;
  uVar3 = _DAT_000075b8;
  *_DAT_000075b4 = _DAT_000075b8;
  *_DAT_000075bc = ~uVar3;
  *_DAT_000075c0 = _DAT_000075c4;
  *_DAT_000075c8 = 0x20000;
  *(bool *)(iVar5 + 9) = -1 < *_DAT_000076a4 << 0xe;
  *_DAT_000075f8 = _DAT_000075cc;
  *_DAT_000075fc = _DAT_000075d0;
  *_DAT_00007600 = _DAT_000075d4;
  puVar4 = _DAT_000075d8;
  *_DAT_00007604 = 4;
  *puVar4 = _DAT_000075dc;
  *_DAT_000075e0 = 0x47;
  *_DAT_00007608 = 4;
  *_DAT_000075e4 = 0x40000000;
  *_DAT_000075e8 = 4;
  func_0x00006fb4();
  func_0x00006bd8();
  FUN_0000575c();
  func_0x00004330();
  func_0x0000725c();
  FUN_0000800c();
                    /* WARNING: Could not recover jumptable at 0x00007596. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)();
  return;
}



// === FUN_00005e04 at 00005e04 (156 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00005e04(uint param_1,uint param_2,uint param_3)

{
  char *pcVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  code *UNRECOVERED_JUMPTABLE;
  undefined1 uStack_1c;
  
  uStack_1c = 0x30;
  if (6 < param_3) goto LAB_00005e98;
  *_DAT_00005ea0 = 1;
  pcVar1 = _DAT_00005ea4;
  *_DAT_00005ea4 = '\0';
  *_DAT_00005ea8 = 1;
  iVar2 = _DAT_00005eb0;
  iVar3 = _DAT_00005eac + param_3 * 9;
  do {
    iVar4 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar3,9);
    if (iVar4 != 0) break;
  } while (*pcVar1 == '\0');
  if (3 < param_2) {
    param_2 = 3;
  }
  if (param_1 == 0) {
LAB_00005e66:
    if (param_1 < 3) goto LAB_00005e6a;
  }
  else {
    if (param_1 == 1) {
      uStack_1c = 0x40;
    }
    else {
      if (param_1 != 2) goto LAB_00005e66;
      uStack_1c = 0x50;
    }
LAB_00005e6a:
    *(undefined1 *)(iVar2 + 0xd) = uStack_1c;
    *(byte *)(iVar2 + 0xe) = (byte)param_2 | 8;
    do {
      iVar3 = FUN_00006b64(*(undefined4 *)(iVar2 + 0x1c),iVar2 + 0xc,3);
      if (iVar3 != 0) break;
    } while (*pcVar1 == '\0');
  }
  if (*pcVar1 != '\0') {
    *_DAT_00005eb4 = _DAT_00005eb8;
  }
LAB_00005e98:
                    /* WARNING: Could not recover jumptable at 0x00005e9e. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)();
  return;
}



// === FUN_00004a94 at 00004a94 (146 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00004a94(int param_1,int param_2,uint param_3)

{
  int iVar1;
  uint extraout_r1;
  uint extraout_r1_00;
  uint extraout_r1_01;
  int extraout_r1_02;
  undefined4 extraout_r1_03;
  uint uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  code *UNRECOVERED_JUMPTABLE;
  
  iVar1 = _DAT_00004b28;
  uVar2 = (uint)*(byte *)(_DAT_00004b30 + 0xf) * 3 + (uint)*(byte *)(_DAT_00004b30 + 0x10);
  iVar3 = 100 - uVar2;
  uVar4 = *_DAT_00004b34;
  if (uVar2 < param_3) {
    uVar5 = (uint)*(char *)(_DAT_00004b2c + param_1 * 0xd + param_2);
    if (uVar5 < *(byte *)(_DAT_00004b28 + 0xc)) {
      func_0x00008574(uVar4 * *(byte *)(_DAT_00004b28 + 0xc),100);
      uVar5 = extraout_r1;
    }
    if (param_3 < 100) {
      func_0x00008574(uVar5 * (param_3 - uVar2),iVar3);
      uVar5 = extraout_r1_00;
    }
  }
  else {
    uVar5 = 0;
  }
  uVar2 = (uint)*(byte *)(iVar1 + 0xb);
  if (uVar4 < uVar2) {
    uVar2 = 0;
  }
  else if ((*(byte *)(iVar1 + 10) <= uVar2) ||
          (func_0x00008574((uVar4 - uVar2) * 100,*(byte *)(iVar1 + 10) - uVar2),
          uVar2 = extraout_r1_01, 100 < extraout_r1_01)) {
    uVar2 = 100;
  }
  func_0x00008574(*(int *)(iVar1 + 0x10) * uVar5,100);
  func_0x00008574(uVar2 * extraout_r1_02,100);
                    /* WARNING: Could not recover jumptable at 0x00004b24. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)(extraout_r1_03);
  return;
}



// === FUN_0000506c at 0000506c (112 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0000506c(void)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  byte extraout_r1;
  uint uVar4;
  code *UNRECOVERED_JUMPTABLE;
  
  iVar2 = func_0x000047b0(0);
  if (iVar2 == 0) {
    uVar3 = 0;
    bVar1 = 0xe4;
  }
  else {
    uVar3 = (uint)*_DAT_000050dc;
    if (uVar3 == 0) {
      uVar3 = 0;
      bVar1 = 0;
    }
    else {
      if (*_DAT_000050e4 <= uVar3) {
        uVar3 = *_DAT_000050e4 - 1 & 0xff;
      }
      bVar1 = (byte)uVar3;
      uVar4 = (int)((*(byte *)(_DAT_000050e8 + 0xf) * uVar3 + (uint)*(byte *)(_DAT_000050e8 + 0x10))
                   * 0x1000000) >> 0x18;
      uVar3 = uVar4 & 0xff;
      if (uVar3 != uVar4) {
        if (uVar3 == 0) {
          bVar1 = 0;
        }
        else {
          func_0x00008584(uVar3 - *(byte *)(_DAT_000050e8 + 0x10));
          bVar1 = extraout_r1;
        }
      }
      if (0xc < *_DAT_000050ec) {
        bVar1 = bVar1 | 0x80;
      }
    }
  }
  *_DAT_000050e0 = bVar1;
                    /* WARNING: Could not recover jumptable at 0x000050da. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)(uVar3);
  return;
}



// === FUN_00008038 at 00008038 (110 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00008038(undefined4 param_1,char *param_2)

{
  undefined1 *puVar1;
  int iVar2;
  undefined1 *puVar3;
  undefined1 *puVar4;
  undefined4 uVar5;
  int iVar6;
  code *UNRECOVERED_JUMPTABLE;
  undefined1 auStack_18 [4];
  
  iVar6 = 0;
  iVar2 = func_0x00007b10();
  puVar1 = _DAT_000081a4;
  if (iVar2 != 0) {
    puVar3 = *(undefined1 **)(_DAT_000081a4 + 0x20);
    if (puVar3 == _DAT_000081a4 + 0x28) {
      puVar4 = _DAT_000081a4 + 0x38;
    }
    else {
      puVar4 = _DAT_000081a4 + 0x28;
    }
    *(undefined1 **)(_DAT_000081a4 + 0x20) = puVar4;
    FUN_00007b1c();
    uVar5 = func_0x00007bf0(puVar3);
    iVar6 = FUN_00007bcc(puVar3,uVar5);
    if (iVar6 == 3) {
      auStack_18[0] = func_0x00007be8(puVar3);
      switch(auStack_18[0]) {
      case 0:
        iVar6 = FUN_00007e64(puVar3,auStack_18,param_1,param_2);
        if (*param_2 != '\0') {
          func_0x00007fd8(puVar1 + 0x58,puVar1 + 0x24,param_1);
          puVar1[9] = 1;
        }
        break;
      case 1:
      case 3:
        iVar6 = FUN_00007e64(puVar3,auStack_18,param_1,param_2);
        break;
      case 2:
        if ((puVar1[0x11] != '\0') && (puVar1[0x12] != '\0')) {
          iVar6 = FUN_00007e64(puVar3,auStack_18,param_1,param_2);
          func_0x00007f58(puVar1 + 0x98,puVar1 + 0x14,param_1,*param_2);
          if (puVar1[0x14] == '\0') {
            puVar1[0x12] = 0;
            func_0x00007b30();
            if ((puVar1[4] != '\0') && (puVar1[0x11] = 0, puVar1[3] != '\0')) {
              puVar1[1] = 1;
            }
          }
        }
        break;
      case 4:
        iVar6 = FUN_00007e64(puVar3,auStack_18,param_1,param_2);
        if (*param_2 != '\0') {
          func_0x00007fd8(puVar1 + 0x48,puVar1 + 6,param_1);
          puVar1[7] = 1;
        }
        break;
      case 5:
        if ((puVar1[0x16] != '\0') && (puVar1[0x17] != '\0')) {
          iVar6 = FUN_00007e64(puVar3,auStack_18,param_1,param_2);
          func_0x00007f58(puVar1 + 0xb8,puVar1 + 0x19,param_1,*param_2);
          if (puVar1[0x19] == '\0') {
            puVar1[0x17] = 0;
            func_0x00007b28();
            if (puVar1[5] != '\0') {
              puVar1[0x16] = 0;
              iVar6 = 6;
              if (puVar1[2] != '\0') {
                *puVar1 = 1;
              }
            }
          }
        }
      }
    }
  }
                    /* WARNING: Could not recover jumptable at 0x000081a0. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)(iVar6);
  return;
}



// === FUN_00008a50 at 00008a50 (108 bytes) ===

/* WARNING: Control flow encountered bad instruction data */

void FUN_00008a50(undefined4 param_1,int param_2,undefined4 param_3,int param_4)

{
  byte extraout_var;
  int iVar1;
  undefined2 *extraout_r1;
  uint uVar2;
  uint uVar3;
  uint unaff_r5;
  uint unaff_r7;
  int in_lr;
  byte bVar4;
  
  if ((uint)(param_2 * 2) < 0x200000) {
    if ((uint)(param_4 * 2) < 0x200000) {
      func_0x000086a8();
      func_0x00008678();
      bVar4 = (byte)unaff_r7 & 1;
      unaff_r7 = unaff_r7 >> 1;
    }
    else {
      func_0x00008678();
      bVar4 = (byte)((uint)param_4 >> 0x1f);
      unaff_r5 = param_4 << 1;
    }
  }
  else {
    func_0x000086a8();
    bVar4 = extraout_var >> 7;
  }
  iVar1 = *(int *)(unaff_r5 + 0x34);
  uRam00000074 = unaff_r5;
  *(undefined1 *)(unaff_r5 + 5) = 0xff;
  uRam4000001c = 0;
  uVar2 = (uint)*(byte *)(unaff_r7 + bVar4 + 0x15);
  *(ushort *)((unaff_r5 >> 0x15) + 0x1c) = (ushort)(unaff_r5 >> 0x15);
  *(uint *)(uVar2 + 0x40) = (uint)*(ushort *)(iVar1 + 0x3c);
  uVar3 = uVar2 << 3;
  iVar1 = ((unaff_r5 >> 0x15) + 2) * 0x10;
  (*(code *)(in_lr + 0xffc))(iVar1,iVar1,uVar3,0x1e);
  uRam00004400 = uVar3 & uVar2 << 4;
  *extraout_r1 = (short)((int)extraout_r1 << 8);
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}



// === FUN_0000601c at 0000601c (100 bytes) ===

/* WARNING: Possible PIC construction at 0x000066c6: Changing call to branch */
/* WARNING: Possible PIC construction at 0x0000684c: Changing call to branch */
/* WARNING: Removing unreachable block (ram,0x000066ca) */
/* WARNING: Removing unreachable block (ram,0x000066ea) */
/* WARNING: Removing unreachable block (ram,0x000066e8) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0000601c(void)

{
  undefined1 *puVar1;
  char *pcVar2;
  char *pcVar3;
  char *pcVar4;
  char *pcVar5;
  char *pcVar6;
  char *pcVar7;
  byte *pbVar8;
  char *pcVar9;
  int iVar10;
  undefined1 uVar11;
  ushort uVar12;
  short sVar13;
  int iVar14;
  byte *pbVar15;
  byte *pbVar16;
  byte *pbVar17;
  undefined1 extraout_r1;
  byte bVar18;
  int extraout_r1_00;
  undefined4 extraout_r1_01;
  undefined4 extraout_r1_02;
  undefined4 extraout_r1_03;
  undefined4 extraout_r1_04;
  undefined1 *puVar19;
  uint uVar20;
  undefined4 *puVar21;
  short *psVar22;
  code *UNRECOVERED_JUMPTABLE;
  bool bVar23;
  uint uStack_2c;
  byte abStack_28 [4];
  undefined1 auStack_24 [16];
  
  iVar14 = FUN_00008038(auStack_24,abStack_28);
  puVar1 = _DAT_000063ac;
  if ((iVar14 != 1) || (uStack_2c = 0, abStack_28[0] == 0)) {
LAB_0000603a:
                    /* WARNING: Could not recover jumptable at 0x00006040. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*UNRECOVERED_JUMPTABLE)();
    return;
  }
LAB_00006058:
  iVar10 = iRam000067cc;
  pcVar9 = pcRam0000670c;
  pbVar8 = pbRam00006708;
  pcVar7 = pcRam00006704;
  pcVar6 = pcRam000063ec;
  pcVar5 = pcRam000063e8;
  pcVar4 = pcRam000063e4;
  pcVar3 = pcRam000063e0;
  pcVar2 = pcRam000063c8;
  pbVar17 = _DAT_000063b8;
  iVar14 = _DAT_000063b4;
  if (abStack_28[0] <= uStack_2c) goto LAB_0000603a;
  pbVar15 = (byte *)(_DAT_000063b4 + 1);
  psVar22 = (short *)(_DAT_000063b4 + 0xc);
  pbVar16 = _DAT_000063b8 + 0x20;
  switch(auStack_24[uStack_2c]) {
  case 9:
    iVar14 = func_0x000047b0(0);
    if ((iVar14 == 0) || (*pbVar15 == *pbRam000063bc)) break;
    bVar18 = *pbRam000063bc & 0x7f;
    *pbVar15 = bVar18;
    if (*pbVar17 <= bVar18) {
      *pbVar15 = *pbVar17 - 1;
    }
    goto code_r0x0000626e;
  case 10:
    if (*pcRam000063c4 != *pcRam000063c0) {
      *pcRam000063c4 = *pcRam000063c0;
      goto code_r0x0000626e;
    }
    break;
  case 0xf:
    bVar18 = *pbRam00006710;
    if (bVar18 < 0xf) {
      if (bVar18 < 5) {
        bVar18 = 5;
      }
    }
    else {
      bVar18 = 0xe;
    }
    *_DAT_000063b8 = bVar18;
    *pbRam00006714 = bVar18;
    puVar19 = puRam00006718;
    func_0x00008584(100,*pbVar17 - 1);
    *puVar19 = extraout_r1;
    puVar19 = puRam0000671c;
    uVar11 = func_0x00008584(100,*pbVar17 - 1);
    *puVar19 = uVar11;
    break;
  case 0x11:
    bVar18 = *pbRam00006720;
    if (0x1e < bVar18) {
      bVar18 = 0x1e;
    }
    _DAT_000063b8[8] = bVar18;
    *pbRam00006724 = bVar18;
    goto code_r0x000064c8;
  case 0x12:
    bVar18 = *pbRam000067a4;
    if (100 < bVar18) {
      bVar18 = 100;
    }
    _DAT_000063b8[10] = bVar18;
    pbVar17 = pbRam000067a8;
    goto code_r0x00006600;
  case 0x13:
    bVar18 = *pbRam000067ac;
    if (100 < bVar18) {
      bVar18 = 100;
    }
    _DAT_000063b8[0xb] = bVar18;
    pbVar17 = pbRam000067b0;
    goto code_r0x0000662a;
  case 0x16:
    bVar18 = *pbRam000067b4;
    uVar20 = (uint)bVar18;
    if (uVar20 < 0x29) {
      if (uVar20 < _DAT_000063b8[0xd] + 1) {
        bVar18 = _DAT_000063b8[0xd] + 5;
      }
      else if (uVar20 < 0x14) {
        bVar18 = 0x14;
      }
    }
    else {
      bVar18 = 0x28;
    }
    _DAT_000063b8[9] = bVar18;
    pbVar17 = pbRam000067b8;
    goto code_r0x000064cc;
  case 0x18:
    if (*pcRam000067c8 == 'U') {
      FUN_00004384();
    }
    break;
  case 0x3b:
    bVar18 = *pbRam0000672c;
    if (0x32 < bVar18) {
      bVar18 = 0x32;
    }
    _DAT_000063b8[0x30] = bVar18;
    *pbRam00006730 = bVar18;
    goto code_r0x000064c8;
  case 0x3c:
    bVar18 = *pbRam00006734;
    if (100 < bVar18) {
      bVar18 = 100;
    }
    _DAT_000063b8[0x31] = bVar18;
    pbVar17 = pbRam00006738;
    goto code_r0x000064f0;
  case 0x3d:
    bVar18 = *pbRam0000673c;
    if (0x50 < bVar18) {
      bVar18 = 0x50;
    }
    _DAT_000063b8[0x32] = bVar18;
    *pbRam00006740 = bVar18;
    puVar21 = puRam00006744;
    func_0x00008584((uint)pbVar17[0x32] << 7,10);
    *puVar21 = extraout_r1_02;
code_r0x000064c8:
    bVar18 = 1;
    pbVar17 = pbRam00006728;
code_r0x000064cc:
    *pbVar17 = bVar18;
    break;
  case 0x3e:
    bVar18 = *pbRam00006748;
    if (0x28 < bVar18) {
      bVar18 = 0x28;
    }
    _DAT_000063b8[0x33] = bVar18;
    *pbRam0000674c = bVar18;
    bVar18 = 1;
    pbVar17 = pbRam00006728;
code_r0x000064f0:
    *pbVar17 = bVar18;
    break;
  case 0x40:
    if (*(char *)(_DAT_000063b4 + 0x2a) != *pcRam000063d4) {
      *(char *)(_DAT_000063b4 + 0x2a) = *pcRam000063d4;
      *puRam000063d8 = 0;
      *puRam000063dc = 0;
      goto code_r0x0000626e;
    }
    break;
  case 0x50:
    if (*(char *)(_DAT_000063b4 + 5) != *pcRam000063e0) {
      *(char *)(_DAT_000063b4 + 5) = *pcRam000063e0;
      *puVar1 = 1;
    }
    if (*(char *)(iVar14 + 6) != pcVar3[1]) {
      *(char *)(iVar14 + 6) = pcVar3[1];
      goto code_r0x0000626e;
    }
    break;
  case 0x51:
    if (*(char *)(_DAT_000063b4 + 7) != *pcRam000063e4) {
      *(char *)(_DAT_000063b4 + 7) = *pcRam000063e4;
      *puVar1 = 1;
    }
    if (*(char *)(iVar14 + 8) != pcVar4[1]) {
      *(char *)(iVar14 + 8) = pcVar4[1];
      goto code_r0x0000626e;
    }
    break;
  case 0x52:
    if (*(char *)(_DAT_000063b4 + 9) != *pcRam000063e8) {
      *(char *)(_DAT_000063b4 + 9) = *pcRam000063e8;
      *puVar1 = 1;
    }
    if (*(char *)(iVar14 + 10) != pcVar5[1]) {
      *(char *)(iVar14 + 10) = pcVar5[1];
      goto code_r0x0000626e;
    }
    break;
  case 0x55:
    uVar20 = (uint)*pbRam000067bc + (uint)pbRam000067bc[1] * 0x100;
    if (uVar20 < uRam000067c0) {
      if (uVar20 < 800) {
        uVar20 = 800;
      }
    }
    else {
      uVar20 = uRam000067c0 - 1;
    }
    *(uint *)(_DAT_000063b8 + 0x10) = uVar20;
    puVar19 = puRam000067c4;
    goto code_r0x00006694;
  case 0x68:
    uVar20 = (uint)*pbRam000067d4 + (uint)pbRam000067d4[1] * 0x100;
    if (uVar20 < uRam000067d8) {
      if (uVar20 < 0xc80) {
        uVar20 = 0xc80;
      }
    }
    else {
      uVar20 = uRam000067d8 - 1;
    }
    *(uint *)(_DAT_000063b8 + 0x14) = uVar20;
    puVar19 = puRam00006a48;
code_r0x00006694:
    *puVar19 = (char)uVar20;
    puVar19[1] = (char)(uVar20 >> 8);
    break;
  case 0x6e:
    bVar18 = *pbRam0000678c;
    if (0x32 < bVar18) {
      bVar18 = 0x32;
    }
    _DAT_000063b8[0xc] = bVar18;
    pbVar17 = pbRam00006790;
    goto code_r0x00006600;
  case 0x6f:
    bVar18 = *pbRam00006794;
    if (bVar18 < 0x65) {
      if (bVar18 == 0) {
        bVar18 = 1;
      }
    }
    else {
      bVar18 = 100;
    }
    _DAT_000063b8[0xe] = bVar18;
    pbVar17 = pbRam00006798;
    goto code_r0x00006600;
  case 0x70:
    bVar18 = *pbRam0000679c;
    if (0x19 < bVar18) {
      bVar18 = 0x19;
    }
    _DAT_000063b8[0xd] = bVar18;
    pbVar17 = pbRam000067a0;
    goto code_r0x0000662a;
  case 0x71:
    bVar18 = *pbRam00006a4c;
    if (bVar18 < 0x97) {
      if (bVar18 < 0x32) {
        bVar18 = 0x32;
      }
    }
    else {
      bVar18 = 0x96;
    }
    _DAT_000063b8[0x18] = bVar18;
    pbVar17 = pbRam00006a50;
    goto code_r0x00006600;
  case 0x72:
    bVar18 = *pbRam00006a54;
    if (bVar18 < 0x97) {
      if (bVar18 < 0x32) {
        bVar18 = 0x32;
      }
    }
    else {
      bVar18 = 0x96;
    }
    _DAT_000063b8[0x19] = bVar18;
    pbVar17 = pbRam00006a58;
    goto code_r0x0000662a;
  case 0x73:
    bVar18 = *pbRam00006a5c;
    if (bVar18 < 0x97) {
      if (bVar18 < 0x32) {
        bVar18 = 0x32;
      }
    }
    else {
      bVar18 = 0x96;
    }
    _DAT_000063b8[0x1a] = bVar18;
    pbVar17 = pbRam00006a60;
    goto code_r0x00006600;
  case 0x74:
    bVar18 = *pbRam00006a64;
    if (bVar18 < 0x97) {
      if (bVar18 < 0x32) {
        bVar18 = 0x32;
      }
    }
    else {
      bVar18 = 0x96;
    }
    _DAT_000063b8[0x1b] = bVar18;
    pbVar17 = pbRam00006a68;
    goto code_r0x0000684a;
  case 0x75:
    bVar18 = *pbRam00006a6c;
    if (bVar18 < 0x97) {
      if (bVar18 < 0x32) {
        bVar18 = 0x32;
      }
    }
    else {
      bVar18 = 0x96;
    }
    _DAT_000063b8[0x1c] = bVar18;
    pbVar17 = pbRam00006a70;
    goto code_r0x00006600;
  case 0x76:
    bVar18 = *pbRam00006a74;
    if (bVar18 < 0x97) {
      if (bVar18 < 0x32) {
        bVar18 = 0x32;
      }
    }
    else {
      bVar18 = 0x96;
    }
    _DAT_000063b8[0x1d] = bVar18;
    pbVar17 = pbRam00006a78;
code_r0x0000662a:
    *pbVar17 = bVar18;
    break;
  case 0x77:
    bVar18 = *pbRam00006a7c;
    if (bVar18 < 0x97) {
      if (bVar18 < 0x32) {
        bVar18 = 0x32;
      }
    }
    else {
      bVar18 = 0x96;
    }
    _DAT_000063b8[0x1e] = bVar18;
    pbVar17 = pbRam00006a80;
code_r0x00006600:
    *pbVar17 = bVar18;
    break;
  case 0x78:
    bVar18 = *pbRam00006a84;
    if (bVar18 < 0x97) {
      if (bVar18 < 0x32) {
        bVar18 = 0x32;
      }
    }
    else {
      bVar18 = 0x96;
    }
    _DAT_000063b8[0x1f] = bVar18;
    pbVar17 = pbRam00006a88;
code_r0x0000684a:
    *pbVar17 = bVar18;
    break;
  case 0x79:
    bVar18 = *pbRam00006a8c;
    if (bVar18 < 0x97) {
      if (bVar18 < 0x32) {
        bVar18 = 0x32;
      }
    }
    else {
      bVar18 = 0x96;
    }
    *pbVar16 = bVar18;
    pbVar16 = (byte *)func_0x0000604c(uRam00006a90);
  case 0x7a:
    bVar18 = *pbRam00006a94;
    if (bVar18 < 0x97) {
      if (bVar18 < 0x32) {
        bVar18 = 0x32;
      }
    }
    else {
      bVar18 = 0x96;
    }
    pbVar16[1] = bVar18;
    pbVar16 = (byte *)func_0x0000604c(uRam00006a98);
code_r0x000068e4:
    bVar18 = *pbRam00006a9c;
    if (bVar18 < 0x97) {
      if (bVar18 < 0x32) {
        bVar18 = 0x32;
      }
    }
    else {
      bVar18 = 0x96;
    }
    pbVar16[2] = bVar18;
    pbVar16 = (byte *)func_0x0000604c(uRam00006aa0);
code_r0x000068fe:
    bVar18 = *pbRam00006aa4;
    if (bVar18 < 0x97) {
      if (bVar18 < 0x32) {
        bVar18 = 0x32;
      }
    }
    else {
      bVar18 = 0x96;
    }
    pbVar16[3] = bVar18;
    pbVar16 = (byte *)func_0x0000604c(uRam00006aa8);
code_r0x00006918:
    bVar18 = *pbRam00006aac;
    if (bVar18 < 0x97) {
      if (bVar18 < 0x32) {
        bVar18 = 0x32;
      }
    }
    else {
      bVar18 = 0x96;
    }
    pbVar16[4] = bVar18;
    pbVar16 = (byte *)func_0x0000604c(uRam00006ab0);
code_r0x00006932:
    bVar18 = *pbRam00006ab4;
    if (bVar18 < 0x97) {
      if (bVar18 < 0x32) {
        bVar18 = 0x32;
      }
    }
    else {
      bVar18 = 0x96;
    }
    pbVar16[5] = bVar18;
    pbVar16 = (byte *)func_0x0000604c(uRam00006ab8);
code_r0x0000694c:
    bVar18 = *pbRam00006abc;
    if (bVar18 < 0x97) {
      if (bVar18 < 0x32) {
        bVar18 = 0x32;
      }
    }
    else {
      bVar18 = 0x96;
    }
    pbVar16[6] = bVar18;
    pbVar16 = (byte *)func_0x0000604c(uRam00006ac0);
code_r0x00006966:
    bVar18 = *pbRam00006ac4;
    if (bVar18 < 0x97) {
      if (bVar18 < 0x32) {
        bVar18 = 0x32;
      }
    }
    else {
      bVar18 = 0x96;
    }
    pbVar16[7] = bVar18;
    pbVar16 = (byte *)func_0x0000604c(uRam00006ac8);
code_r0x00006980:
    bVar18 = *pbRam00006acc;
    if (bVar18 < 0x97) {
      if (bVar18 < 0x32) {
        bVar18 = 0x32;
      }
    }
    else {
      bVar18 = 0x96;
    }
    pbVar16[8] = bVar18;
    pbVar16 = (byte *)func_0x0000604c(uRam00006ad0);
code_r0x0000699a:
    bVar18 = *pbRam00006ad4;
    if (bVar18 < 0x97) {
      if (bVar18 < 0x32) {
        bVar18 = 0x32;
      }
    }
    else {
      bVar18 = 0x96;
    }
    pbVar16[9] = bVar18;
    pbVar16 = (byte *)func_0x0000604c(uRam00006ad8);
code_r0x000069b4:
    bVar18 = *pbRam00006adc;
    if (bVar18 < 0x97) {
      if (bVar18 < 0x32) {
        bVar18 = 0x32;
      }
    }
    else {
      bVar18 = 0x96;
    }
    pbVar16[10] = bVar18;
    pbVar16 = (byte *)func_0x0000604c(uRam00006ae0);
code_r0x000069ce:
    bVar18 = *pbRam00006ae4;
    if (bVar18 < 0x97) {
      if (bVar18 < 0x32) {
        bVar18 = 0x32;
      }
    }
    else {
      bVar18 = 0x96;
    }
    pbVar16[0xb] = bVar18;
    pbVar16 = (byte *)func_0x0000604c(uRam00006ae8);
code_r0x000069e8:
    bVar18 = *pbRam00006aec;
    if (bVar18 < 0x97) {
      if (bVar18 < 0x32) {
        bVar18 = 0x32;
      }
    }
    else {
      bVar18 = 0x96;
    }
    pbVar16[0xc] = bVar18;
    pbVar16 = (byte *)func_0x0000604c(uRam00006af0);
code_r0x00006a02:
    bVar18 = *pbRam00006af4;
    if (bVar18 < 0x97) {
      if (bVar18 < 0x32) {
        bVar18 = 0x32;
      }
    }
    else {
      bVar18 = 0x96;
    }
    pbVar16[0xd] = bVar18;
    pbVar16 = (byte *)func_0x0000604c(uRam00006af8);
code_r0x00006a1c:
    bVar18 = *pbRam00006afc;
    if (bVar18 < 0x97) {
      if (bVar18 < 0x32) {
        bVar18 = 0x32;
      }
    }
    else {
      bVar18 = 0x96;
    }
    pbVar16[0xe] = bVar18;
    func_0x0000604c(uRam00006b00);
code_r0x00006a36:
    if (*pbRam00006b04 < 0x97) {
      func_0x00006042();
    }
    func_0x00006048();
    uVar20 = (uint)psVar22 >> 0x1a;
code_r0x00006b08:
                    /* WARNING: Could not recover jumptable at 0x00006b0a. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*pcRam00006b0c)(psVar22,uVar20);
    return;
  case 0x7b:
    goto code_r0x000068e4;
  case 0x7c:
    goto code_r0x000068fe;
  case 0x7d:
    goto code_r0x00006918;
  case 0x7e:
    goto code_r0x00006932;
  case 0x7f:
    goto code_r0x0000694c;
  case 0x80:
    goto code_r0x00006966;
  case 0x81:
    goto code_r0x00006980;
  case 0x82:
    goto code_r0x0000699a;
  case 0x83:
    goto code_r0x000069b4;
  case 0x84:
    goto code_r0x000069ce;
  case 0x85:
    goto code_r0x000069e8;
  case 0x86:
    goto code_r0x00006a02;
  case 0x87:
    goto code_r0x00006a1c;
  case 0x88:
    goto code_r0x00006a36;
  case 0x89:
    uVar20 = (uint)*pbRam00006750 + (uint)pbRam00006750[1] * 0x100;
    if (300 < uVar20) {
      uVar20 = 300;
    }
    *(uint *)(_DAT_000063b8 + 0x34) = uVar20;
    puVar19 = puRam00006754;
    *puRam00006754 = (char)uVar20;
    puVar19[1] = (char)(uVar20 >> 8);
    iVar14 = *(int *)(pbVar17 + 0x34);
    puVar21 = puRam00006758;
    goto code_r0x0000654c;
  case 0x8a:
    uVar20 = (uint)*pbRam0000675c + (uint)pbRam0000675c[1] * 0x100;
    if (300 < uVar20) {
      uVar20 = 300;
    }
    *(uint *)(_DAT_000063b8 + 0x38) = uVar20;
    puVar19 = puRam00006760;
    *puRam00006760 = (char)uVar20;
    puVar19[1] = (char)(uVar20 >> 8);
    iVar14 = *(int *)(pbVar17 + 0x38);
    puVar21 = puRam00006764;
    goto code_r0x0000654c;
  case 0x8b:
    uVar20 = (uint)*pbRam00006768 + (uint)pbRam00006768[1] * 0x100;
    if (300 < uVar20) {
      uVar20 = 300;
    }
    *(uint *)(_DAT_000063b8 + 0x3c) = uVar20;
    puVar19 = puRam0000676c;
    *puRam0000676c = (char)uVar20;
    puVar19[1] = (char)(uVar20 >> 8);
    iVar14 = *(int *)(pbVar17 + 0x3c);
    puVar21 = puRam00006770;
    goto code_r0x0000659e;
  case 0x8c:
    uVar20 = (uint)*pbRam00006774 + (uint)pbRam00006774[1] * 0x100;
    if (300 < uVar20) {
      uVar20 = 300;
    }
    *(uint *)(_DAT_000063b8 + 0x40) = uVar20;
    puVar19 = puRam00006778;
    *puRam00006778 = (char)uVar20;
    puVar19[1] = (char)(uVar20 >> 8);
    iVar14 = *(int *)(pbVar17 + 0x40);
    puVar21 = puRam0000677c;
code_r0x0000654c:
    func_0x00008574(iVar14 << 7,10);
    *puVar21 = extraout_r1_03;
    break;
  case 0x8d:
    uVar20 = (uint)*pbRam00006780 + (uint)pbRam00006780[1] * 0x100;
    if (300 < uVar20) {
      uVar20 = 300;
    }
    *(uint *)(_DAT_000063b8 + 4) = uVar20;
    puVar19 = puRam00006784;
    *puRam00006784 = (char)uVar20;
    puVar19[1] = (char)(uVar20 >> 8);
    iVar14 = *(int *)(pbVar17 + 4);
    puVar21 = puRam00006788;
code_r0x0000659e:
    func_0x00008574(iVar14 << 7,10);
    *puVar21 = extraout_r1_04;
    break;
  case 0x92:
    goto code_r0x000062b6;
  case 0x96:
    if (*(char *)(_DAT_000063b4 + 0xb) != *pcRam000063ec) {
      *(char *)(_DAT_000063b4 + 0xb) = *pcRam000063ec;
      *puVar1 = 1;
    }
    sVar13 = (ushort)(byte)pcVar6[1] + (ushort)(byte)pcVar6[2] * 0x100;
    if (*psVar22 != sVar13) {
      *psVar22 = sVar13;
      goto code_r0x0000626e;
    }
    break;
  case 0x97:
    if (*(char *)(_DAT_000063b4 + 0xe) != *pcRam00006704) {
      *(char *)(_DAT_000063b4 + 0xe) = *pcRam00006704;
      *puVar1 = 1;
    }
    sVar13 = (ushort)(byte)pcVar7[1] + (ushort)(byte)pcVar7[2] * 0x100;
    if (*(short *)(iVar14 + 0x10) != sVar13) {
      *(short *)(iVar14 + 0x10) = sVar13;
      goto code_r0x0000626e;
    }
    break;
  case 0x98:
    bVar18 = *pbRam00006708;
    uVar20 = bVar18 & 1;
    if (*(byte *)(_DAT_000063b4 + 0x13) != uVar20) {
      *(char *)(_DAT_000063b4 + 0x13) = (char)uVar20;
      *puVar1 = 1;
    }
    bVar23 = (int)((uint)bVar18 << 0x1e) < 0;
    if ((bool)*(char *)(iVar14 + 0x12) != bVar23) {
      *(bool *)(iVar14 + 0x12) = bVar23;
      *puVar1 = 1;
    }
    sVar13 = (ushort)pbVar8[1] + (ushort)pbVar8[2] * 0x100;
    if (*(short *)(iVar14 + 0x14) != sVar13) {
      *(short *)(iVar14 + 0x14) = sVar13;
      goto code_r0x0000626e;
    }
    break;
  case 0x99:
    if (*(char *)(_DAT_000063b4 + 0x16) != *pcRam0000670c) {
      *(char *)(_DAT_000063b4 + 0x16) = *pcRam0000670c;
      *puVar1 = 1;
    }
    sVar13 = (ushort)(byte)pcVar9[1] + (ushort)(byte)pcVar9[2] * 0x100;
    if (*(short *)(iVar14 + 0x18) != sVar13) {
      *(short *)(iVar14 + 0x18) = sVar13;
      goto code_r0x0000626e;
    }
    break;
  case 0x9a:
    if (*(char *)(_DAT_000063b4 + 3) != *pcRam000063c8) {
      *(char *)(_DAT_000063b4 + 3) = *pcRam000063c8;
      *puVar1 = 1;
    }
    uVar12 = (ushort)(byte)pcVar2[1] + (ushort)(byte)pcVar2[2] * 0x100;
    if (*(byte *)(iVar14 + 4) != uVar12) {
      *(char *)(iVar14 + 4) = (char)uVar12;
      *puVar1 = 1;
    }
    goto code_r0x000062b6;
  case 0xe2:
    if (*(byte *)(iRam000067cc + 1) < 3) {
      *(byte *)(_DAT_000063b4 + 0x1a) = *(byte *)(iRam000067cc + 1);
    }
    if (*(byte *)(iVar10 + 2) < 5) {
      *(byte *)(iVar14 + 0x1b) = *(byte *)(iVar10 + 2);
    }
    uVar20 = (uint)*(byte *)(iVar10 + 3);
    psVar22 = (short *)(uVar20 + (uint)*(byte *)(iVar10 + 4) * 0x100);
    goto code_r0x00006b08;
  }
LAB_0000604e:
  uStack_2c = uStack_2c + 1 & 0xff;
  goto LAB_00006058;
code_r0x000062b6:
  pcVar2 = pcRam000063cc;
  if (*(char *)(iVar14 + 0x28) != *pcRam000063cc) {
    *(char *)(iVar14 + 0x28) = *pcRam000063cc;
    *puRam000063d0 = 0;
    *puVar1 = 1;
  }
  bVar18 = pcVar2[1];
  if ((uint)*(byte *)(iVar14 + 0x29) != (uint)bVar18) {
    *(byte *)(iVar14 + 0x29) = bVar18;
    func_0x00008584((uint)bVar18 * 0x7d,100);
    *(int *)(puVar1 + 4) = extraout_r1_00;
    func_0x00008574(extraout_r1_00 * 0x19,100);
    *(undefined4 *)(puVar1 + 8) = extraout_r1_01;
code_r0x0000626e:
    *puVar1 = 1;
  }
  goto LAB_0000604e;
}



// === FUN_000048e8 at 000048e8 (90 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000048e8(undefined4 param_1,int param_2)

{
  int extraout_r1;
  int iVar1;
  int iVar2;
  int iVar3;
  code *UNRECOVERED_JUMPTABLE;
  
  iVar1 = _DAT_00004950;
  iVar2 = *(int *)(_DAT_00004950 + 0x54);
  if (*_DAT_00004954 == '\0') goto LAB_00004938;
  *_DAT_00004954 = '\0';
  *_DAT_00004944 = 1;
  *_DAT_00004948 = 1;
  iVar3 = 0x4b0 - *_DAT_00004958;
  if ((*(char *)(iVar1 + 9) == '\0') || (param_2 != 0)) {
LAB_0000492a:
    iVar2 = 0;
  }
  else {
    func_0x00008584(iVar3,0x28);
    iVar2 = (iVar2 + extraout_r1 + iVar3) - *(int *)(iVar1 + 0x58);
    if (iVar2 < 0) goto LAB_0000492a;
    if (_DAT_0000494c <= iVar2) {
      iVar2 = _DAT_0000494c + -1;
    }
  }
  *(int *)(iVar1 + 0x58) = iVar3;
LAB_00004938:
  *(int *)(iVar1 + 0x54) = iVar2;
                    /* WARNING: Could not recover jumptable at 0x00004940. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)(iVar2);
  return;
}



// === FUN_00007e64 at 00007e64 (80 bytes) ===

void FUN_00007e64(byte *param_1,byte *param_2,undefined4 param_3,undefined1 *param_4)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  code *UNRECOVERED_JUMPTABLE;
  
  *param_2 = 6;
  *param_4 = 0;
  bVar1 = *param_1;
  if ((bVar1 & 0xf) == 0) {
    uVar3 = 5;
  }
  else {
    iVar2 = func_0x00007b60(param_1,(bVar1 & 0xf) + 1);
    if (iVar2 == 0x3b) {
      *param_2 = bVar1 >> 4;
      uVar3 = FUN_00007cc4(param_1 + 1,(bVar1 & 0xf) - 1,bVar1 >> 4,param_3,param_4);
    }
    else {
      uVar3 = 4;
    }
  }
                    /* WARNING: Could not recover jumptable at 0x00007eb2. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)(uVar3);
  return;
}



// === FUN_000073e4 at 000073e4 (74 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000073e4(void)

{
  uint uVar1;
  code *UNRECOVERED_JUMPTABLE;
  
  if (_UndefinedInstruction != *_DAT_00007430 + 0x1000) {
    uVar1 = 0;
    do {
      ((undefined4 *)(uVar1 * 4))[0x80000] = *(undefined4 *)(uVar1 * 4);
      uVar1 = uVar1 + 1;
    } while (uVar1 < 0x20);
    uVar1 = 1;
    do {
      *(int *)(uVar1 * 4 + 0x200000) = *(int *)(uVar1 * 4 + 0x104000) + 0x1000;
      uVar1 = uVar1 + 1;
    } while (uVar1 < 6);
    FUN_00006b20(0,0x80,0x200000);
  }
                    /* WARNING: Could not recover jumptable at 0x0000742c. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)(0x200000);
  return;
}



// === FUN_00007eb4 at 00007eb4 (72 bytes) ===

void FUN_00007eb4(byte *param_1,int param_2,undefined4 param_3,char *param_4)

{
  char cVar1;
  byte bVar2;
  undefined4 uVar3;
  byte bVar4;
  code *UNRECOVERED_JUMPTABLE;
  
  *param_1 = (byte)(param_2 << 4) | *param_1 & 0xf;
  cVar1 = FUN_00007d80(param_1 + 1,param_2,param_3,param_4);
  bVar4 = cVar1 + 1;
  *param_1 = bVar4 & 0xf | *param_1 & 0xf0;
  bVar2 = func_0x00007b60(param_1,(uint)bVar4);
  param_1[bVar4] = bVar2;
  if (*param_4 == '\0') {
    uVar3 = 1;
  }
  else {
    uVar3 = 2;
  }
                    /* WARNING: Could not recover jumptable at 0x00007efa. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)(uVar3);
  return;
}



// === FUN_00008970 at 00008970 (64 bytes) ===

void FUN_00008970(int param_1,uint param_2,int param_3,uint param_4)

{
  uint uVar1;
  
  uVar1 = param_2 * 2;
  if (uVar1 < 0xffe00001) {
    uVar1 = param_4 * 2;
  }
  if (0xffe00000 < uVar1) {
    *pbRam0000896c = *pbRam0000896c | 1;
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

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00005ebc(void)

{
  byte bVar1;
  byte *pbVar2;
  code *UNRECOVERED_JUMPTABLE;
  
  if (*_DAT_00005ef4 != '\0') {
    *_DAT_00005ef4 = '\0';
    *_DAT_00005ef8 = 1;
    *_DAT_00005efc = 1;
    pbVar2 = _DAT_00005f00;
    bVar1 = *_DAT_00005f00;
    *_DAT_00005f00 = bVar1 + 1;
    if (6 < (byte)(bVar1 + 1)) {
      *pbVar2 = 0;
    }
    FUN_00005e04(0,0,*pbVar2);
  }
                    /* WARNING: Could not recover jumptable at 0x00005ef0. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)();
  return;
}



// === FUN_00006b9c at 00006b9c (54 bytes) ===

void FUN_00006b9c(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  code *UNRECOVERED_JUMPTABLE;
  
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
                    /* WARNING: Could not recover jumptable at 0x00006bd0. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)(iVar1);
  return;
}



// === FUN_00007c1c at 00007c1c (54 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_00007c1c(uint param_1)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  if (param_1 < 0x4b) {
    uVar1 = *(undefined4 *)(_DAT_00007c54 + param_1 * 4);
  }
  else {
    iVar2 = _DAT_00007cb4;
    iVar3 = _DAT_00007c58;
    if (((0x95 < param_1) && (iVar2 = _DAT_00007cb8, iVar3 = _DAT_00007c5c, 0xb8 < param_1)) &&
       (iVar2 = _DAT_00007cc0, iVar3 = _DAT_00007c64, param_1 < 0xdc)) {
      iVar2 = _DAT_00007cbc;
      iVar3 = _DAT_00007c60;
    }
    uVar1 = *(undefined4 *)(iVar3 + param_1 * 4 + iVar2);
  }
  return uVar1;
}



// === FUN_00007c68 at 00007c68 (54 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_00007c68(uint param_1)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  if (param_1 < 0x4b) {
    uVar1 = *(undefined4 *)(_DAT_00007ca0 + param_1 * 4);
  }
  else {
    iVar2 = _DAT_00007cb4;
    iVar3 = _DAT_00007ca4;
    if (((0x95 < param_1) && (iVar2 = _DAT_00007cb8, iVar3 = _DAT_00007ca8, 0xb8 < param_1)) &&
       (iVar2 = _DAT_00007cc0, iVar3 = _DAT_00007cb0, param_1 < 0xdc)) {
      iVar2 = _DAT_00007cbc;
      iVar3 = _DAT_00007cac;
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

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00004114(void)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 *puVar3;
  code *UNRECOVERED_JUMPTABLE;
  
  puVar1 = _DAT_00004148;
  puVar3 = _DAT_00004144;
  if (_DAT_00004144 < _DAT_00004148) {
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
                    /* WARNING: Could not recover jumptable at 0x00004126. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)();
  return;
}



// === FUN_00007efc at 00007efc (44 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00007efc(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  code *UNRECOVERED_JUMPTABLE;
  
  iVar1 = _DAT_00008034;
  if ((*(char *)(_DAT_00008034 + 0xe) == '\0') && (*(char *)(_DAT_00008034 + 0xf) == '\0')) {
    *(undefined1 *)(_DAT_00008034 + 0xe) = 1;
    func_0x00007fd8(iVar1 + 0x78,iVar1 + 0xd,param_1,param_2);
    uVar2 = 1;
  }
  else {
    uVar2 = 0;
  }
                    /* WARNING: Could not recover jumptable at 0x00007f26. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)(uVar2);
  return;
}



// === FUN_00006b64 at 00006b64 (40 bytes) ===

void FUN_00006b64(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  code *UNRECOVERED_JUMPTABLE;
  
  iVar1 = FUN_00006b48();
  if (iVar1 != 0) {
    *(undefined4 *)(param_1 + 0x120) = 0x100;
    *(undefined4 *)(param_1 + 0x108) = param_2;
    *(undefined4 *)(param_1 + 0x10c) = param_3;
    iVar1 = 1;
  }
                    /* WARNING: Could not recover jumptable at 0x00006b8a. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)(iVar1);
  return;
}



// === FUN_0000800c at 0000800c (40 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0000800c(void)

{
  int iVar1;
  code *UNRECOVERED_JUMPTABLE;
  
  iVar1 = _DAT_00008034;
  *(undefined1 *)(_DAT_00008034 + 7) = 0;
  *(undefined1 *)(iVar1 + 8) = 0;
  *(undefined1 *)(iVar1 + 9) = 0;
  *(undefined1 *)(iVar1 + 0xb) = 0;
  *(undefined1 *)(iVar1 + 0xc) = 0;
  *(undefined1 *)(iVar1 + 0xe) = 0;
  *(undefined1 *)(iVar1 + 0xf) = 0;
  *(undefined1 *)(iVar1 + 0x11) = 0;
  *(undefined1 *)(iVar1 + 0x12) = 0;
  *(undefined1 *)(iVar1 + 0x15) = 0;
  *(undefined1 *)(iVar1 + 0x16) = 0;
  *(undefined1 *)(iVar1 + 0x17) = 0;
  FUN_00007b1c(*(undefined4 *)(iVar1 + 0x20));
                    /* WARNING: Could not recover jumptable at 0x00008032. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)();
  return;
}



// === FUN_00006b20 at 00006b20 (36 bytes) ===

void FUN_00006b20(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  code *UNRECOVERED_JUMPTABLE;
  
  func_0x00200c84();
  func_0x00007498();
  func_0x00200c94(param_1,param_2,param_3);
  func_0x000074b4();
                    /* WARNING: Could not recover jumptable at 0x00006b42. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)();
  return;
}



// === FUN_0000b18c at 0000b18c (36 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0000b18c(void)

{
  code *UNRECOVERED_JUMPTABLE;
  
  uRamffffff60 = _DAT_0000b1b4;
  uRamffffff64 = _DAT_0000b1b0;
  func_0x0000b114();
                    /* WARNING: Could not recover jumptable at 0x0000b1ae. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)(uRamffffff68 & 0x10);
  return;
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



// === FUN_0000497c at 0000497c (30 bytes) ===

void FUN_0000497c(void)

{
  int iVar1;
  uint uVar2;
  uint extraout_r1;
  code *UNRECOVERED_JUMPTABLE;
  
  iVar1 = FUN_0000495c();
  func_0x00008584(iVar1 * 0x13,100);
  uVar2 = extraout_r1 & 0xff;
  if (0x13 < uVar2) {
    uVar2 = 0x13;
  }
                    /* WARNING: Could not recover jumptable at 0x00004998. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)(uVar2);
  return;
}



// === FUN_00004028 at 00004028 (28 bytes) ===

void FUN_00004028(code *param_1)

{
  int in_lr;
  
  (*param_1)();
                    /* WARNING: Could not recover jumptable at 0x00004040. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)(in_lr + -4))();
  return;
}



// === FUN_0000495c at 0000495c (28 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0000495c(uint param_1)

{
  uint extraout_r1;
  code *UNRECOVERED_JUMPTABLE;
  
  if (_DAT_00004978 + 1 <= param_1) {
    param_1 = _DAT_00004978;
  }
  func_0x00008574(param_1 * 100);
                    /* WARNING: Could not recover jumptable at 0x00004976. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)(extraout_r1 & 0xff);
  return;
}



// === FUN_0000571c at 0000571c (26 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

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
  *_DAT_00005738 = uVar1;
  return;
}



// === FUN_00005f14 at 00005f14 (26 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00005f14(void)

{
  code *UNRECOVERED_JUMPTABLE;
  
  if (*_DAT_00005f30 == -0x5b) {
    FUN_00008530(_DAT_00006018,_DAT_00005f30,0x2c);
  }
  func_0x00005f34();
                    /* WARNING: Could not recover jumptable at 0x00005f2c. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)();
  return;
}



// === FUN_00007bcc at 00007bcc (26 bytes) ===

void FUN_00007bcc(undefined4 param_1,char param_2)

{
  int iVar1;
  undefined4 uVar2;
  code *UNRECOVERED_JUMPTABLE;
  
  iVar1 = func_0x00007b60(param_1,param_2 + '\x01');
  if (iVar1 == 0x3b) {
    uVar2 = 3;
  }
  else {
    uVar2 = 4;
  }
                    /* WARNING: Could not recover jumptable at 0x00007be4. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)(uVar2);
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



// === FUN_00006b48 at 00006b48 (24 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_00006b48(int param_1)

{
  undefined4 uVar1;
  
  if ((*(int *)(param_1 + 0x10) << 0x1a < 0) && (*_DAT_00006b60 << 0x14 < 0)) {
    uVar1 = 1;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}



// === FUN_0000893c at 0000893c (24 bytes) ===

bool FUN_0000893c(void)

{
  undefined1 in_ZR;
  
  FUN_00008908();
  return !(bool)in_ZR;
}



// === FUN_000089b0 at 000089b0 (24 bytes) ===

undefined1 FUN_000089b0(void)

{
  undefined1 in_CY;
  
  FUN_00008970();
  return in_CY;
}



// === FUN_0000854c at 0000854c (22 bytes) ===

void FUN_0000854c(undefined1 *param_1,undefined1 param_2,int param_3)

{
  if (param_3 != 0) {
    do {
      *param_1 = param_2;
      param_1 = param_1 + 1;
      param_3 = param_3 + -1;
    } while (param_3 != 0);
  }
  return;
}



// === FUN_00004044 at 00004044 (16 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00004044(void)

{
  int iVar1;
  char *pcVar2;
  undefined4 uVar3;
  int unaff_r4;
  byte *unaff_r5;
  char unaff_r6;
  char *unaff_r7;
  
  iVar1 = iRam000040f8;
  uVar3 = (*(code *)0x4e74)(uRam000040fc);
  *(undefined4 *)(unaff_r5 + 0x10) = uVar3;
  *unaff_r7 = unaff_r6;
  *unaff_r5 = *unaff_r5 & 0xbf;
  if (unaff_r4 << 0x18 < 0) {
    uVar3 = func_0x00007364(*_DAT_00004328);
    pcVar2 = _DAT_0000432c;
    if (*_DAT_0000432c != '\0') {
      uVar3 = func_0x000041f0(unaff_r5 + 0x114,uVar3);
      *(undefined4 *)(unaff_r5 + 0xc) = uVar3;
      *pcVar2 = unaff_r6;
    }
    *unaff_r5 = *unaff_r5 & 0x7f;
  }
  if (*unaff_r5 == 0) {
    *unaff_r5 = 0xf8;
    *_DAT_0000437c = 2;
  }
                    /* WARNING: Could not recover jumptable at 0x00004300. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (**(code **)(iVar1 + 0x10))();
  return;
}



// === FUN_00006b8c at 00006b8c (16 bytes) ===

bool FUN_00006b8c(int param_1)

{
  return *(int *)(param_1 + 0x10) << 0x1b < 0;
}



// === FUN_0000409c at 0000409c (12 bytes) ===

/* WARNING: Control flow encountered bad instruction data */

void FUN_0000409c(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}



// === FUN_00007b1c at 00007b1c (12 bytes) ===

void FUN_00007b1c(undefined4 param_1)

{
  code *UNRECOVERED_JUMPTABLE;
  
  func_0x0000720c(param_1,0x10);
                    /* WARNING: Could not recover jumptable at 0x00007b26. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)();
  return;
}



// === FUN_00007af8 at 00007af8 (10 bytes) ===

void FUN_00007af8(void)

{
  code *UNRECOVERED_JUMPTABLE;
  
  func_0x000071d0();
                    /* WARNING: Could not recover jumptable at 0x00007b00. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)();
  return;
}



// === FUN_00004094 at 00004094 (8 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00004094(void)

{
  *puRam00004368 = uRam0000436c;
  *puRam00004370 = 0xf8;
  *_DAT_0000437c = 2;
  *_DAT_00004380 = 0xf8;
  *puRam00004374 = 1;
  *puRam00004378 = 1;
  return;
}



// === FUN_000040b4 at 000040b4 (8 bytes) ===

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000040b4(int param_1,int param_2,byte *param_3,code *param_4)

{
  byte bVar1;
  undefined1 *puVar2;
  int iVar3;
  undefined1 uVar4;
  undefined4 uVar5;
  undefined4 extraout_r1;
  undefined4 extraout_r1_00;
  undefined4 extraout_r1_01;
  undefined4 extraout_r1_02;
  undefined4 extraout_r1_03;
  undefined4 extraout_r1_04;
  undefined1 *unaff_r4;
  undefined1 unaff_r5;
  int unaff_r6;
  code *UNRECOVERED_JUMPTABLE;
  
  *(int *)(param_2 + param_1) = unaff_r6;
  unaff_r4[2] = unaff_r5;
  unaff_r4[3] = 0x83;
  unaff_r4[4] = 0x86;
  unaff_r4[5] = 0x89;
  unaff_r4[6] = 0x8c;
  unaff_r4[7] = 0x8f;
  unaff_r4[8] = 0x92;
  unaff_r4[9] = 0x95;
  uVar4 = (undefined1)param_2;
  unaff_r4[10] = uVar4;
  unaff_r4[0xb] = uVar4;
  unaff_r4[0xc] = uVar4;
  unaff_r4[0xd] = uVar4;
  unaff_r4[0xe] = uVar4;
  unaff_r4[0xf] = uVar4;
  iVar3 = _DAT_0000463c;
  *(char *)(_DAT_0000463c + 0xf) = (char)param_1;
  UNRECOVERED_JUMPTABLE = param_4;
  uVar4 = func_0x00008584(100,*param_3 - 1,param_3,param_4,param_1,param_2,param_3,param_4,
                          &stack0x00000000);
  *(undefined1 *)(iVar3 + 0x10) = uVar4;
  *_DAT_0000459c = *param_3;
  puVar2 = _DAT_000045a0;
  uVar5 = *(undefined4 *)(param_3 + 4);
  *_DAT_000045a0 = (char)uVar5;
  puVar2[1] = (char)((uint)uVar5 >> 8);
  puVar2 = _DAT_000045a4;
  uVar5 = *(undefined4 *)(unaff_r4 + 0x14);
  *_DAT_000045a4 = (char)uVar5;
  puVar2[1] = (char)((uint)uVar5 >> 8);
  puVar2 = _DAT_000045a8;
  uVar5 = *(undefined4 *)(unaff_r4 + 0x18);
  *_DAT_000045a8 = (char)uVar5;
  puVar2[1] = (char)((uint)uVar5 >> 8);
  puVar2 = _DAT_000045ac;
  uVar5 = *(undefined4 *)(unaff_r4 + 0x1c);
  *_DAT_000045ac = (char)uVar5;
  puVar2[1] = (char)((uint)uVar5 >> 8);
  puVar2 = _DAT_000045b0;
  uVar5 = *(undefined4 *)(unaff_r4 + 0x20);
  *_DAT_000045b0 = (char)uVar5;
  puVar2[1] = (char)((uint)uVar5 >> 8);
  *_DAT_00004640 = param_3[8];
  *_DAT_000045b4 = param_3[10];
  *_DAT_000045b8 = param_3[0xb];
  *_DAT_00004644 = (char)unaff_r6;
  *_DAT_000045bc = unaff_r4[0x11];
  *_DAT_00004648 = (char)unaff_r6;
  *_DAT_0000464c = unaff_r4[0x13];
  *_DAT_000045c0 = param_3[9];
  puVar2 = _DAT_000045c4;
  uVar5 = *(undefined4 *)(param_3 + 0x10);
  *_DAT_000045c4 = (char)uVar5;
  puVar2[1] = (char)((uint)uVar5 >> 8);
  puVar2 = _DAT_000045c8;
  uVar5 = *(undefined4 *)(param_3 + 0x14);
  *_DAT_000045c8 = (char)uVar5;
  puVar2[1] = (char)((uint)uVar5 >> 8);
  uVar4 = SUB41(param_4,0);
  *_DAT_000045cc = uVar4;
  *_DAT_000045d0 = param_3[0xe];
  *_DAT_000045d4 = param_3[0xd];
  *_DAT_000045d8 = param_3[0x18];
  *_DAT_000045dc = param_3[0x19];
  *_DAT_000045e0 = param_3[0x1a];
  *_DAT_000045e4 = param_3[0x1b];
  *_DAT_000045e8 = param_3[0x1c];
  *_DAT_000045ec = param_3[0x1d];
  *_DAT_000045f0 = param_3[0x1e];
  *_DAT_000045f4 = param_3[0x1f];
  *_DAT_000045f8 = *unaff_r4;
  *_DAT_000045fc = unaff_r4[1];
  *_DAT_00004600 = unaff_r4[2];
  *_DAT_00004604 = unaff_r4[3];
  *_DAT_00004608 = unaff_r4[4];
  *_DAT_0000460c = unaff_r4[5];
  *_DAT_00004610 = unaff_r4[6];
  *_DAT_00004614 = unaff_r4[7];
  *_DAT_00004618 = unaff_r4[8];
  *_DAT_0000461c = unaff_r4[9];
  bVar1 = unaff_r4[10];
  *_DAT_00004620 = bVar1;
  *_DAT_00004624 = bVar1;
  *_DAT_00004628 = bVar1;
  *_DAT_0000462c = bVar1;
  *_DAT_00004630 = bVar1;
  *_DAT_00004634 = bVar1;
  func_0x00008574((uint)bVar1 << 7,10);
  *(undefined4 *)(iVar3 + 0x34) = extraout_r1;
  func_0x00008574(*(int *)(unaff_r4 + 0x18) << 7,10);
  *(undefined4 *)(iVar3 + 0x38) = extraout_r1_00;
  func_0x00008574(*(int *)(unaff_r4 + 0x1c) << 7,10);
  *(undefined4 *)(iVar3 + 0x3c) = extraout_r1_01;
  func_0x00008574(*(int *)(unaff_r4 + 0x20) << 7,10);
  *(undefined4 *)(iVar3 + 0x40) = extraout_r1_02;
  func_0x00008574(*(int *)(param_3 + 4) << 7,10);
  *(undefined4 *)(iVar3 + 0x44) = extraout_r1_03;
  func_0x00008584(unaff_r6 << 7,10);
  *(undefined4 *)(iVar3 + 0x48) = extraout_r1_04;
  *(undefined1 *)(iVar3 + 1) = uVar4;
  *(undefined1 *)(iVar3 + 2) = 1;
                    /* WARNING: Could not recover jumptable at 0x00004594. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)();
  return;
}

