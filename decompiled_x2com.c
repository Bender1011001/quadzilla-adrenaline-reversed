// === x2com_xmit at 00107d50 (3354 bytes) ===

undefined8 x2com_xmit(undefined8 param_1,undefined8 param_2)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined8 uVar6;
  undefined8 uVar7;
  undefined8 uVar8;
  undefined8 uVar9;
  undefined8 uVar10;
  undefined *puVar11;
  undefined *puVar12;
  undefined *puVar13;
  undefined *puVar14;
  undefined *puVar15;
  undefined *puVar16;
  undefined *puVar17;
  undefined *puVar18;
  undefined *puVar19;
  undefined *puVar20;
  undefined *puVar21;
  char *pcVar22;
  char cVar23;
  byte bVar24;
  uint uVar25;
  ulong uVar26;
  undefined *puVar27;
  undefined8 uVar28;
  byte bVar29;
  undefined *puVar30;
  ulong uVar31;
  undefined *puVar32;
  long lVar33;
  long lVar34;
  ulong uVar35;
  byte bVar36;
  byte bVar37;
  long in_FS_OFFSET;
  char local_46 [14];
  long local_38;
  
  local_38 = *(long *)(in_FS_OFFSET + 0x28);
  cVar23 = x2com_is_tx_ready();
  pcVar22 = DAT_0010cf38;
  puVar21 = PTR_0010cf28;
  puVar20 = PTR_0010cf20;
  puVar19 = PTR_0010cf10;
  puVar18 = PTR_0010cee0;
  puVar17 = PTR_0010ced0;
  puVar16 = PTR_0010cec8;
  puVar15 = PTR_0010cea8;
  puVar14 = PTR_0010ce78;
  puVar13 = PTR_0010ce70;
  puVar12 = PTR_0010ce68;
  puVar11 = PTR_0010ce48;
  puVar30 = PTR_0010ce40;
  puVar32 = PTR_0010ce38;
  puVar27 = PTR_0010ce28;
  if (cVar23 == '\0') {
    uVar28 = 8;
    goto LAB_00107eb1;
  }
  if (*PTR_0010ced0 != '\0') {
    x2com_build_msg(PTR_0010cf28,2,PTR_0010cef8,PTR_0010cf00);
    cVar23 = x2com_get_msg_last_pos(puVar21);
    x2com_tx_msg(param_1,param_2,puVar21,cVar23 + '\x01');
    *puVar17 = 0;
    uVar28 = 9;
    goto LAB_00107eb1;
  }
  if (*PTR_0010cec8 == '\0') {
    if (*PTR_0010cec0 == '\0') {
      if (*PTR_0010ce28 == '\0') {
        if (*PTR_0010ce20 == '\0') {
          if (*PTR_0010cee0 == '\0') {
            if (*PTR_0010ced8 == '\0') {
              if ((*PTR_0010cea8 == '\0' & *PTR_0010ce48) == 0) {
                if (*PTR_0010ce40 != '\0') {
                  __android_log_print(6,"BluetoothChatService","x2com_xmit - cwa needed");
                  *puVar30 = 0;
                  *PTR_0010ceb8 = 0;
                  *PTR_0010cea0 = 0;
                  *PTR_0010ceb0 = 0;
                  puVar30 = PTR_0010cef0;
                  puVar32 = PTR_0010ce58;
                  puVar27 = PTR_0010ce50;
                  bVar37 = *PTR_0010ce58;
                  if (bVar37 != 0) {
                    bVar36 = 0xe;
                    if (bVar37 < 0xe) {
                      bVar36 = bVar37;
                    }
                    if (bVar36 != 0) {
                      uVar26 = (ulong)(byte)(bVar36 - 1) + 1;
                      if (uVar26 < 0x20) {
                        uVar25 = 0;
                      }
                      else {
                        uVar25 = (uint)uVar26 & 0xffffffe0;
                        uVar35 = (ulong)uVar25;
                        lVar34 = (uVar35 - 0x20 >> 5) + 1;
                        uVar31 = (ulong)((uint)lVar34 & 1);
                        if (uVar35 - 0x20 == 0) {
                          lVar33 = 0;
                        }
                        else {
                          lVar34 = uVar31 - lVar34;
                          lVar33 = 0;
                          do {
                            puVar2 = (undefined4 *)(puVar27 + lVar33);
                            uVar3 = puVar2[1];
                            uVar4 = puVar2[2];
                            uVar5 = puVar2[3];
                            uVar28 = *(undefined8 *)(puVar27 + lVar33 + 0x10);
                            uVar6 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x10) + 8);
                            uVar7 = *(undefined8 *)(puVar27 + lVar33 + 0x20);
                            uVar8 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x20) + 8);
                            uVar9 = *(undefined8 *)(puVar27 + lVar33 + 0x30);
                            uVar10 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x30) + 8);
                            puVar1 = (undefined4 *)(puVar30 + lVar33);
                            *puVar1 = *puVar2;
                            puVar1[1] = uVar3;
                            puVar1[2] = uVar4;
                            puVar1[3] = uVar5;
                            *(undefined8 *)(puVar30 + lVar33 + 0x10) = uVar28;
                            *(undefined8 *)((long)(puVar30 + lVar33 + 0x10) + 8) = uVar6;
                            *(undefined8 *)(puVar30 + lVar33 + 0x20) = uVar7;
                            *(undefined8 *)((long)(puVar30 + lVar33 + 0x20) + 8) = uVar8;
                            *(undefined8 *)(puVar30 + lVar33 + 0x30) = uVar9;
                            *(undefined8 *)((long)(puVar30 + lVar33 + 0x30) + 8) = uVar10;
                            lVar33 = lVar33 + 0x40;
                            lVar34 = lVar34 + 2;
                          } while (lVar34 != 0);
                        }
                        puVar27 = PTR_0010cef0;
                        if (uVar31 != 0) {
                          puVar1 = (undefined4 *)(PTR_0010ce50 + lVar33);
                          uVar3 = puVar1[1];
                          uVar4 = puVar1[2];
                          uVar5 = puVar1[3];
                          uVar28 = *(undefined8 *)(PTR_0010ce50 + lVar33 + 0x10);
                          uVar6 = *(undefined8 *)((long)(PTR_0010ce50 + lVar33 + 0x10) + 8);
                          puVar2 = (undefined4 *)(PTR_0010cef0 + lVar33);
                          *puVar2 = *puVar1;
                          puVar2[1] = uVar3;
                          puVar2[2] = uVar4;
                          puVar2[3] = uVar5;
                          *(undefined8 *)(puVar27 + lVar33 + 0x10) = uVar28;
                          *(undefined8 *)((long)(puVar27 + lVar33 + 0x10) + 8) = uVar6;
                        }
                        if (uVar26 == uVar35) goto LAB_001085e0;
                        puVar27 = PTR_0010ce50 + uVar35;
                        puVar30 = PTR_0010cef0 + uVar35;
                      }
                      lVar34 = 0;
                      do {
                        puVar30[lVar34] = puVar27[lVar34];
                        lVar34 = lVar34 + 1;
                      } while ((byte)((char)uVar25 + (char)lVar34) < bVar36);
                    }
LAB_001085e0:
                    *PTR_0010cee8 = bVar36;
                  }
                  puVar30 = PTR_0010cf28;
                  puVar27 = PTR_0010ce50;
                  x2com_build_msg(PTR_0010cf28,0,PTR_0010ce50);
                  cVar23 = x2com_get_msg_last_pos(puVar30);
                  x2com_tx_msg(param_1,param_2,puVar30,cVar23 + '\x01');
                  x2com_start_ack_timer(param_1,param_2);
                  puVar30 = PTR_0010cea8;
                  bVar37 = *puVar32;
                  if (bVar37 == 0) {
                    *PTR_0010ceb0 = 1;
                    *puVar11 = 1;
                    *puVar30 = 1;
                    uVar28 = 0x10;
                  }
                  else {
                    *puVar11 = 1;
                    *puVar30 = 1;
                    bVar36 = *PTR_0010cee8;
                    uVar28 = 0x11;
                    if ((ulong)bVar36 != 0) {
                      bVar24 = 0xe;
                      if (bVar37 < 0xe) {
                        bVar24 = bVar37;
                      }
                      uVar26 = 0;
                      bVar29 = 0;
                      do {
                        cVar23 = PTR_0010cef0[uVar26];
                        uVar31 = 1;
                        do {
                          lVar34 = uVar31 - 1;
                          if (bVar24 <= uVar31) break;
                          uVar31 = uVar31 + 1;
                        } while (cVar23 != puVar27[lVar34]);
                        if (cVar23 != puVar27[lVar34]) {
                          uVar31 = (ulong)bVar29;
                          bVar29 = bVar29 + 1;
                          local_46[uVar31] = cVar23;
                        }
                        uVar26 = uVar26 + 1;
                      } while (uVar26 != bVar36);
                      if (bVar29 != 0) goto LAB_001086ce;
                    }
                  }
                  goto LAB_001086eb;
                }
                if ((*PTR_0010ce88 == '\0' & *PTR_0010ce68) == 0) {
                  if (*PTR_0010ce60 == '\0') {
                    uVar28 = 0;
                    goto LAB_00107eb1;
                  }
                  *PTR_0010ce60 = 0;
                  *PTR_0010ce98 = 0;
                  *PTR_0010ce80 = 0;
                  *PTR_0010ce90 = 0;
                  puVar30 = PTR_0010cf10;
                  puVar32 = PTR_0010ce78;
                  puVar27 = PTR_0010ce70;
                  bVar37 = *PTR_0010ce78;
                  if (bVar37 != 0) {
                    bVar36 = 0xe;
                    if (bVar37 < 0xe) {
                      bVar36 = bVar37;
                    }
                    if (bVar36 != 0) {
                      uVar26 = (ulong)(byte)(bVar36 - 1) + 1;
                      if (uVar26 < 0x20) {
                        uVar25 = 0;
                      }
                      else {
                        uVar25 = (uint)uVar26 & 0xffffffe0;
                        uVar31 = (ulong)uVar25;
                        lVar34 = (uVar31 - 0x20 >> 5) + 1;
                        uVar35 = (ulong)((uint)lVar34 & 1);
                        if (uVar31 - 0x20 == 0) {
                          lVar33 = 0;
                        }
                        else {
                          lVar34 = uVar35 - lVar34;
                          lVar33 = 0;
                          do {
                            puVar2 = (undefined4 *)(puVar27 + lVar33);
                            uVar3 = puVar2[1];
                            uVar4 = puVar2[2];
                            uVar5 = puVar2[3];
                            uVar28 = *(undefined8 *)(puVar27 + lVar33 + 0x10);
                            uVar6 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x10) + 8);
                            uVar7 = *(undefined8 *)(puVar27 + lVar33 + 0x20);
                            uVar8 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x20) + 8);
                            uVar9 = *(undefined8 *)(puVar27 + lVar33 + 0x30);
                            uVar10 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x30) + 8);
                            puVar1 = (undefined4 *)(puVar30 + lVar33);
                            *puVar1 = *puVar2;
                            puVar1[1] = uVar3;
                            puVar1[2] = uVar4;
                            puVar1[3] = uVar5;
                            *(undefined8 *)(puVar30 + lVar33 + 0x10) = uVar28;
                            *(undefined8 *)((long)(puVar30 + lVar33 + 0x10) + 8) = uVar6;
                            *(undefined8 *)(puVar30 + lVar33 + 0x20) = uVar7;
                            *(undefined8 *)((long)(puVar30 + lVar33 + 0x20) + 8) = uVar8;
                            *(undefined8 *)(puVar30 + lVar33 + 0x30) = uVar9;
                            *(undefined8 *)((long)(puVar30 + lVar33 + 0x30) + 8) = uVar10;
                            lVar33 = lVar33 + 0x40;
                            lVar34 = lVar34 + 2;
                          } while (lVar34 != 0);
                        }
                        puVar27 = PTR_0010cf10;
                        if (uVar35 != 0) {
                          puVar1 = (undefined4 *)(PTR_0010ce70 + lVar33);
                          uVar3 = puVar1[1];
                          uVar4 = puVar1[2];
                          uVar5 = puVar1[3];
                          uVar28 = *(undefined8 *)(PTR_0010ce70 + lVar33 + 0x10);
                          uVar6 = *(undefined8 *)((long)(PTR_0010ce70 + lVar33 + 0x10) + 8);
                          puVar2 = (undefined4 *)(PTR_0010cf10 + lVar33);
                          *puVar2 = *puVar1;
                          puVar2[1] = uVar3;
                          puVar2[2] = uVar4;
                          puVar2[3] = uVar5;
                          *(undefined8 *)(puVar27 + lVar33 + 0x10) = uVar28;
                          *(undefined8 *)((long)(puVar27 + lVar33 + 0x10) + 8) = uVar6;
                        }
                        if (uVar26 == uVar31) goto LAB_00108936;
                        puVar27 = PTR_0010ce70 + uVar31;
                        puVar30 = PTR_0010cf10 + uVar31;
                      }
                      lVar34 = 0;
                      do {
                        puVar30[lVar34] = puVar27[lVar34];
                        lVar34 = lVar34 + 1;
                      } while ((byte)((char)uVar25 + (char)lVar34) < bVar36);
                    }
LAB_00108936:
                    *PTR_0010cf08 = bVar36;
                  }
                  puVar30 = PTR_0010cf28;
                  puVar27 = PTR_0010ce70;
                  x2com_build_msg(PTR_0010cf28,4,PTR_0010ce70,puVar32);
                  cVar23 = x2com_get_msg_last_pos(puVar30);
                  x2com_tx_msg(param_1,param_2,puVar30,cVar23 + '\x01');
                  x2com_start_resp_timer(param_1,param_2);
                  bVar37 = *puVar32;
                  if (bVar37 == 0) {
                    *PTR_0010ce90 = 1;
                    *puVar12 = 1;
                    *PTR_0010ce88 = 1;
                    uVar28 = 0x12;
                  }
                  else {
                    *puVar12 = 1;
                    *PTR_0010ce88 = 1;
                    bVar36 = *PTR_0010cf08;
                    uVar28 = 0x13;
                    if ((ulong)bVar36 != 0) {
                      bVar24 = 0xe;
                      if (bVar37 < 0xe) {
                        bVar24 = bVar37;
                      }
                      uVar26 = 0;
                      bVar29 = 0;
                      do {
                        cVar23 = PTR_0010cf10[uVar26];
                        uVar31 = 1;
                        do {
                          lVar34 = uVar31 - 1;
                          if (bVar24 <= uVar31) break;
                          uVar31 = uVar31 + 1;
                        } while (cVar23 != puVar27[lVar34]);
                        if (cVar23 != puVar27[lVar34]) {
                          uVar31 = (ulong)bVar29;
                          bVar29 = bVar29 + 1;
                          local_46[uVar31] = cVar23;
                        }
                        uVar26 = uVar26 + 1;
                      } while (uVar26 != bVar36);
                      if (bVar29 != 0) goto LAB_00108a29;
                    }
                  }
LAB_00108a4d:
                  bVar29 = 0;
                }
                else {
                  bVar37 = *PTR_0010ce78;
                  if (bVar37 != 0) {
                    bVar36 = 0xe;
                    if (bVar37 < 0xe) {
                      bVar36 = bVar37;
                    }
                    if (bVar36 != 0) {
                      uVar26 = (ulong)(byte)(bVar36 - 1) + 1;
                      if (uVar26 < 0x20) {
                        uVar25 = 0;
                        puVar27 = PTR_0010ce70;
                        puVar32 = PTR_0010cf10;
                      }
                      else {
                        uVar25 = (uint)uVar26 & 0xffffffe0;
                        uVar31 = (ulong)uVar25;
                        lVar34 = (uVar31 - 0x20 >> 5) + 1;
                        uVar35 = (ulong)((uint)lVar34 & 1);
                        if (uVar31 - 0x20 == 0) {
                          lVar33 = 0;
                        }
                        else {
                          lVar34 = uVar35 - lVar34;
                          lVar33 = 0;
                          do {
                            puVar2 = (undefined4 *)(puVar13 + lVar33);
                            uVar3 = puVar2[1];
                            uVar4 = puVar2[2];
                            uVar5 = puVar2[3];
                            uVar28 = *(undefined8 *)(puVar13 + lVar33 + 0x10);
                            uVar6 = *(undefined8 *)((long)(puVar13 + lVar33 + 0x10) + 8);
                            uVar7 = *(undefined8 *)(puVar13 + lVar33 + 0x20);
                            uVar8 = *(undefined8 *)((long)(puVar13 + lVar33 + 0x20) + 8);
                            uVar9 = *(undefined8 *)(puVar13 + lVar33 + 0x30);
                            uVar10 = *(undefined8 *)((long)(puVar13 + lVar33 + 0x30) + 8);
                            puVar1 = (undefined4 *)(puVar19 + lVar33);
                            *puVar1 = *puVar2;
                            puVar1[1] = uVar3;
                            puVar1[2] = uVar4;
                            puVar1[3] = uVar5;
                            *(undefined8 *)(puVar19 + lVar33 + 0x10) = uVar28;
                            *(undefined8 *)((long)(puVar19 + lVar33 + 0x10) + 8) = uVar6;
                            *(undefined8 *)(puVar19 + lVar33 + 0x20) = uVar7;
                            *(undefined8 *)((long)(puVar19 + lVar33 + 0x20) + 8) = uVar8;
                            *(undefined8 *)(puVar19 + lVar33 + 0x30) = uVar9;
                            *(undefined8 *)((long)(puVar19 + lVar33 + 0x30) + 8) = uVar10;
                            lVar33 = lVar33 + 0x40;
                            lVar34 = lVar34 + 2;
                          } while (lVar34 != 0);
                        }
                        puVar27 = PTR_0010cf10;
                        if (uVar35 != 0) {
                          puVar1 = (undefined4 *)(PTR_0010ce70 + lVar33);
                          uVar3 = puVar1[1];
                          uVar4 = puVar1[2];
                          uVar5 = puVar1[3];
                          uVar28 = *(undefined8 *)(PTR_0010ce70 + lVar33 + 0x10);
                          uVar6 = *(undefined8 *)((long)(PTR_0010ce70 + lVar33 + 0x10) + 8);
                          puVar2 = (undefined4 *)(PTR_0010cf10 + lVar33);
                          *puVar2 = *puVar1;
                          puVar2[1] = uVar3;
                          puVar2[2] = uVar4;
                          puVar2[3] = uVar5;
                          *(undefined8 *)(puVar27 + lVar33 + 0x10) = uVar28;
                          *(undefined8 *)((long)(puVar27 + lVar33 + 0x10) + 8) = uVar6;
                        }
                        if (uVar26 == uVar31) goto LAB_001087cc;
                        puVar27 = PTR_0010ce70 + uVar31;
                        puVar32 = PTR_0010cf10 + uVar31;
                      }
                      lVar34 = 0;
                      do {
                        puVar32[lVar34] = puVar27[lVar34];
                        lVar34 = lVar34 + 1;
                      } while ((byte)((char)uVar25 + (char)lVar34) < bVar36);
                    }
LAB_001087cc:
                    *PTR_0010cf08 = bVar36;
                  }
                  puVar32 = PTR_0010cf28;
                  puVar27 = PTR_0010ce70;
                  x2com_build_msg(PTR_0010cf28,4,PTR_0010ce70,puVar14);
                  cVar23 = x2com_get_msg_last_pos(puVar32);
                  x2com_tx_msg(param_1,param_2,puVar32,cVar23 + '\x01');
                  x2com_start_resp_timer(param_1,param_2);
                  bVar37 = *puVar14;
                  if ((bVar37 == 0) || (uVar28 = 0x13, bVar37 == DAT_0010d014)) {
                    *PTR_0010ce90 = 1;
                    uVar28 = 0x12;
                  }
                  *PTR_0010ce88 = 1;
                  if ((bVar37 == 0) || (bVar36 = *PTR_0010cf08, (ulong)bVar36 == 0))
                  goto LAB_00108a4d;
                  bVar24 = 0xe;
                  if (bVar37 < 0xe) {
                    bVar24 = bVar37;
                  }
                  uVar26 = 0;
                  bVar29 = 0;
                  do {
                    cVar23 = PTR_0010cf10[uVar26];
                    uVar31 = 1;
                    do {
                      lVar34 = uVar31 - 1;
                      if (bVar24 <= uVar31) break;
                      uVar31 = uVar31 + 1;
                    } while (cVar23 != puVar27[lVar34]);
                    if (cVar23 != puVar27[lVar34]) {
                      uVar31 = (ulong)bVar29;
                      bVar29 = bVar29 + 1;
                      local_46[uVar31] = cVar23;
                    }
                    uVar26 = uVar26 + 1;
                  } while (uVar26 != bVar36);
                  if (bVar29 == 0) goto LAB_00108a4d;
LAB_00108a29:
                  memcpy(PTR_0010cf10,local_46,(ulong)bVar29);
                }
                *PTR_0010cf08 = bVar29;
                DAT_0010d014 = bVar37;
                goto LAB_00107eb1;
              }
              __android_log_print(6,"BluetoothChatService","x2com_xmit - cwa progress");
              puVar30 = PTR_0010cef0;
              puVar32 = PTR_0010ce58;
              puVar27 = PTR_0010ce50;
              bVar37 = *PTR_0010ce58;
              if (bVar37 != 0) {
                bVar36 = 0xe;
                if (bVar37 < 0xe) {
                  bVar36 = bVar37;
                }
                if (bVar36 != 0) {
                  uVar26 = (ulong)(byte)(bVar36 - 1) + 1;
                  if (uVar26 < 0x20) {
                    uVar25 = 0;
                  }
                  else {
                    uVar25 = (uint)uVar26 & 0xffffffe0;
                    uVar31 = (ulong)uVar25;
                    lVar34 = (uVar31 - 0x20 >> 5) + 1;
                    uVar35 = (ulong)((uint)lVar34 & 1);
                    if (uVar31 - 0x20 == 0) {
                      lVar33 = 0;
                    }
                    else {
                      lVar34 = uVar35 - lVar34;
                      lVar33 = 0;
                      do {
                        puVar2 = (undefined4 *)(puVar27 + lVar33);
                        uVar3 = puVar2[1];
                        uVar4 = puVar2[2];
                        uVar5 = puVar2[3];
                        uVar28 = *(undefined8 *)(puVar27 + lVar33 + 0x10);
                        uVar6 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x10) + 8);
                        uVar7 = *(undefined8 *)(puVar27 + lVar33 + 0x20);
                        uVar8 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x20) + 8);
                        uVar9 = *(undefined8 *)(puVar27 + lVar33 + 0x30);
                        uVar10 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x30) + 8);
                        puVar1 = (undefined4 *)(puVar30 + lVar33);
                        *puVar1 = *puVar2;
                        puVar1[1] = uVar3;
                        puVar1[2] = uVar4;
                        puVar1[3] = uVar5;
                        *(undefined8 *)(puVar30 + lVar33 + 0x10) = uVar28;
                        *(undefined8 *)((long)(puVar30 + lVar33 + 0x10) + 8) = uVar6;
                        *(undefined8 *)(puVar30 + lVar33 + 0x20) = uVar7;
                        *(undefined8 *)((long)(puVar30 + lVar33 + 0x20) + 8) = uVar8;
                        *(undefined8 *)(puVar30 + lVar33 + 0x30) = uVar9;
                        *(undefined8 *)((long)(puVar30 + lVar33 + 0x30) + 8) = uVar10;
                        lVar33 = lVar33 + 0x40;
                        lVar34 = lVar34 + 2;
                      } while (lVar34 != 0);
                    }
                    puVar27 = PTR_0010cef0;
                    if (uVar35 != 0) {
                      puVar1 = (undefined4 *)(PTR_0010ce50 + lVar33);
                      uVar3 = puVar1[1];
                      uVar4 = puVar1[2];
                      uVar5 = puVar1[3];
                      uVar28 = *(undefined8 *)(PTR_0010ce50 + lVar33 + 0x10);
                      uVar6 = *(undefined8 *)((long)(PTR_0010ce50 + lVar33 + 0x10) + 8);
                      puVar2 = (undefined4 *)(PTR_0010cef0 + lVar33);
                      *puVar2 = *puVar1;
                      puVar2[1] = uVar3;
                      puVar2[2] = uVar4;
                      puVar2[3] = uVar5;
                      *(undefined8 *)(puVar27 + lVar33 + 0x10) = uVar28;
                      *(undefined8 *)((long)(puVar27 + lVar33 + 0x10) + 8) = uVar6;
                    }
                    if (uVar26 == uVar31) goto LAB_001083fe;
                    puVar27 = PTR_0010ce50 + uVar31;
                    puVar30 = PTR_0010cef0 + uVar31;
                  }
                  lVar34 = 0;
                  do {
                    puVar30[lVar34] = puVar27[lVar34];
                    lVar34 = lVar34 + 1;
                  } while ((byte)((char)uVar25 + (char)lVar34) < bVar36);
                }
LAB_001083fe:
                *PTR_0010cee8 = bVar36;
              }
              puVar30 = PTR_0010cf28;
              puVar27 = PTR_0010ce50;
              x2com_build_msg(PTR_0010cf28,0,PTR_0010ce50,puVar32);
              cVar23 = x2com_get_msg_last_pos(puVar30);
              x2com_tx_msg(param_1,param_2,puVar30,cVar23 + '\x01');
              x2com_start_ack_timer(param_1,param_2);
              bVar37 = *puVar32;
              if ((bVar37 == 0) || (uVar28 = 0x11, bVar37 == DAT_0010d013)) {
                *PTR_0010ceb0 = 1;
                uVar28 = 0x10;
              }
              *puVar15 = 1;
              if ((bVar37 == 0) || (bVar36 = *PTR_0010cee8, (ulong)bVar36 == 0)) {
LAB_001086eb:
                bVar29 = 0;
              }
              else {
                bVar24 = 0xe;
                if (bVar37 < 0xe) {
                  bVar24 = bVar37;
                }
                uVar26 = 0;
                bVar29 = 0;
                do {
                  cVar23 = PTR_0010cef0[uVar26];
                  uVar31 = 1;
                  do {
                    lVar34 = uVar31 - 1;
                    if (bVar24 <= uVar31) break;
                    uVar31 = uVar31 + 1;
                  } while (cVar23 != puVar27[lVar34]);
                  if (cVar23 != puVar27[lVar34]) {
                    uVar31 = (ulong)bVar29;
                    bVar29 = bVar29 + 1;
                    local_46[uVar31] = cVar23;
                  }
                  uVar26 = uVar26 + 1;
                } while (uVar26 != bVar36);
                if (bVar29 == 0) goto LAB_001086eb;
LAB_001086ce:
                memcpy(PTR_0010cef0,local_46,(ulong)bVar29);
              }
              *PTR_0010cee8 = bVar29;
              DAT_0010d013 = bVar37;
              goto LAB_00107eb1;
            }
            *PTR_0010ced8 = 0;
            pcVar22 = DAT_0010cf38;
            puVar27 = PTR_0010cf28;
            x2com_build_msg(PTR_0010cf28,3,PTR_0010cf30,DAT_0010cf38);
            cVar23 = x2com_get_msg_last_pos(puVar27);
            x2com_tx_msg(param_1,param_2,puVar27,cVar23 + '\x01');
            cVar23 = *pcVar22;
            if (cVar23 == '\0') {
              uVar28 = 0xe;
              goto LAB_00107eb1;
            }
            *puVar18 = 1;
          }
          else {
            x2com_build_msg(PTR_0010cf28,3,PTR_0010cf30,DAT_0010cf38);
            cVar23 = x2com_get_msg_last_pos(puVar21);
            x2com_tx_msg(param_1,param_2,puVar21,cVar23 + '\x01');
            cVar23 = *pcVar22;
            if ((cVar23 == '\0') || (cVar23 == DAT_0010d012)) {
              *puVar18 = 0;
              uVar28 = 0xe;
              goto LAB_00107eb1;
            }
          }
          uVar28 = 0xf;
          DAT_0010d012 = cVar23;
          goto LAB_00107eb1;
        }
        *PTR_0010ce20 = 0;
        puVar30 = PTR_0010cf28;
        puVar32 = PTR_0010ce38;
        x2com_build_msg(PTR_0010cf28,1,PTR_0010ce30,PTR_0010ce38);
        cVar23 = x2com_get_msg_last_pos(puVar30);
        x2com_tx_msg(param_1,param_2,puVar30,cVar23 + '\x01');
        cVar23 = *puVar32;
        if (cVar23 == '\0') {
          uVar28 = 0xc;
          goto LAB_00107eb1;
        }
        *puVar27 = 1;
      }
      else {
        x2com_build_msg(PTR_0010cf28,1,PTR_0010ce30,PTR_0010ce38);
        cVar23 = x2com_get_msg_last_pos(puVar21);
        x2com_tx_msg(param_1,param_2,puVar21,cVar23 + '\x01');
        cVar23 = *puVar32;
        if ((cVar23 == '\0') || (cVar23 == DAT_0010d011)) {
          *puVar27 = 0;
          uVar28 = 0xc;
          goto LAB_00107eb1;
        }
      }
      uVar28 = 0xd;
      DAT_0010d011 = cVar23;
      goto LAB_00107eb1;
    }
    *PTR_0010cec0 = 0;
    puVar32 = PTR_0010cf28;
    puVar27 = PTR_0010cf20;
    x2com_build_msg(PTR_0010cf28,5,PTR_0010cf18,PTR_0010cf20);
    cVar23 = x2com_get_msg_last_pos(puVar32);
    x2com_tx_msg(param_1,param_2,puVar32,cVar23 + '\x01');
    cVar23 = *puVar27;
    if (cVar23 == '\0') {
      uVar28 = 10;
      goto LAB_00107eb1;
    }
    *puVar16 = 1;
  }
  else {
    x2com_build_msg(PTR_0010cf28,5,PTR_0010cf18,PTR_0010cf20);
    cVar23 = x2com_get_msg_last_pos(puVar21);
    x2com_tx_msg(param_1,param_2,puVar21,cVar23 + '\x01');
    cVar23 = *puVar20;
    if ((cVar23 == '\0') || (cVar23 == DAT_0010d010)) {
      *puVar16 = 0;
      uVar28 = 10;
      goto LAB_00107eb1;
    }
  }
  uVar28 = 0xb;
  DAT_0010d010 = cVar23;
LAB_00107eb1:
  if (*(long *)(in_FS_OFFSET + 0x28) != local_38) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return uVar28;
}



// === x2com_rcv at 001076f0 (1609 bytes) ===

int x2com_rcv(undefined8 param_1,undefined8 param_2,undefined *param_3,byte *param_4)

{
  char cVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined1 uVar5;
  int iVar6;
  undefined1 *puVar7;
  byte bVar8;
  uint uVar9;
  long lVar10;
  byte bVar11;
  ulong uVar12;
  ulong uVar13;
  undefined *puVar14;
  ulong uVar15;
  undefined *puVar16;
  long lVar17;
  byte bVar18;
  byte *pbVar19;
  long in_FS_OFFSET;
  undefined4 local_4c;
  char local_46 [14];
  long local_38;
  
  local_38 = *(long *)(in_FS_OFFSET + 0x28);
  uVar5 = x2com_get_msg_last_pos(param_3);
  iVar6 = x2com_check_crc(param_3,uVar5);
  if (iVar6 != 3) goto switchD_00107762_default;
  local_4c = x2com_get_msg_type(param_3);
  puVar14 = PTR_0010ce68;
  iVar6 = 3;
  switch(local_4c) {
  case 0:
    iVar6 = x2com_parse_msg(param_3,&local_4c,param_3,param_4);
    puVar14 = PTR_0010cef8;
    bVar11 = *param_4;
    if (bVar11 == 0) goto switchD_00107762_default;
    bVar18 = 0xe;
    if (bVar11 < 0xe) {
      bVar18 = bVar11;
    }
    if (bVar18 != 0) {
      uVar13 = (ulong)(byte)(bVar18 - 1);
      uVar15 = uVar13 + 1;
      if ((uVar15 < 0x20) ||
         ((PTR_0010cef8 < param_3 + uVar13 + 1 && (param_3 < PTR_0010cef8 + uVar13 + 1)))) {
        uVar9 = 0;
      }
      else {
        uVar9 = (uint)uVar15 & 0xffffffe0;
        uVar13 = (ulong)uVar9;
        lVar10 = (uVar13 - 0x20 >> 5) + 1;
        uVar12 = (ulong)((uint)lVar10 & 3);
        if (uVar13 - 0x20 < 0x60) {
          lVar17 = 0;
          puVar16 = PTR_0010cef8;
        }
        else {
          lVar10 = uVar12 - lVar10;
          lVar17 = 0;
          do {
            uVar2 = *(undefined8 *)((long)(param_3 + lVar17) + 8);
            uVar3 = *(undefined8 *)(param_3 + lVar17 + 0x10);
            uVar4 = *(undefined8 *)((long)(param_3 + lVar17 + 0x10) + 8);
            *(undefined8 *)(puVar14 + lVar17) = *(undefined8 *)(param_3 + lVar17);
            *(undefined8 *)((long)(puVar14 + lVar17) + 8) = uVar2;
            *(undefined8 *)(puVar14 + lVar17 + 0x10) = uVar3;
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x10) + 8) = uVar4;
            uVar2 = *(undefined8 *)((long)(param_3 + lVar17 + 0x20) + 8);
            uVar3 = *(undefined8 *)(param_3 + lVar17 + 0x30);
            uVar4 = *(undefined8 *)((long)(param_3 + lVar17 + 0x30) + 8);
            *(undefined8 *)(puVar14 + lVar17 + 0x20) = *(undefined8 *)(param_3 + lVar17 + 0x20);
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x20) + 8) = uVar2;
            *(undefined8 *)(puVar14 + lVar17 + 0x30) = uVar3;
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x30) + 8) = uVar4;
            uVar2 = *(undefined8 *)((long)(param_3 + lVar17 + 0x40) + 8);
            uVar3 = *(undefined8 *)(param_3 + lVar17 + 0x50);
            uVar4 = *(undefined8 *)((long)(param_3 + lVar17 + 0x50) + 8);
            *(undefined8 *)(puVar14 + lVar17 + 0x40) = *(undefined8 *)(param_3 + lVar17 + 0x40);
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x40) + 8) = uVar2;
            *(undefined8 *)(puVar14 + lVar17 + 0x50) = uVar3;
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x50) + 8) = uVar4;
            uVar2 = *(undefined8 *)((long)(param_3 + lVar17 + 0x60) + 8);
            uVar3 = *(undefined8 *)(param_3 + lVar17 + 0x70);
            uVar4 = *(undefined8 *)((long)(param_3 + lVar17 + 0x70) + 8);
            *(undefined8 *)(puVar14 + lVar17 + 0x60) = *(undefined8 *)(param_3 + lVar17 + 0x60);
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x60) + 8) = uVar2;
            *(undefined8 *)(puVar14 + lVar17 + 0x70) = uVar3;
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x70) + 8) = uVar4;
            lVar17 = lVar17 + 0x80;
            lVar10 = lVar10 + 4;
            puVar16 = PTR_0010cef8;
          } while (lVar10 != 0);
        }
        PTR_0010cef8 = puVar16;
        if (uVar12 != 0) {
          lVar17 = lVar17 + 0x10;
          lVar10 = -uVar12;
          do {
            uVar2 = *(undefined8 *)((long)(param_3 + lVar17 + -0x10) + 8);
            uVar3 = *(undefined8 *)(param_3 + lVar17);
            uVar4 = *(undefined8 *)((long)(param_3 + lVar17) + 8);
            *(undefined8 *)(puVar16 + lVar17 + -0x10) = *(undefined8 *)(param_3 + lVar17 + -0x10);
            *(undefined8 *)((long)(puVar16 + lVar17 + -0x10) + 8) = uVar2;
            *(undefined8 *)(puVar16 + lVar17) = uVar3;
            *(undefined8 *)((long)(puVar16 + lVar17) + 8) = uVar4;
            lVar17 = lVar17 + 0x20;
            lVar10 = lVar10 + 1;
          } while (lVar10 != 0);
        }
        if (uVar15 == uVar13) goto LAB_001078e3;
        param_3 = param_3 + uVar13;
        puVar14 = PTR_0010cef8 + uVar13;
      }
      lVar10 = 0;
      do {
        puVar14[lVar10] = param_3[lVar10];
        lVar10 = lVar10 + 1;
      } while ((byte)((char)uVar9 + (char)lVar10) < bVar18);
    }
LAB_001078e3:
    *PTR_0010cf00 = bVar18;
    puVar7 = PTR_0010ced0;
    break;
  case 1:
  case 3:
    iVar6 = x2com_parse_msg(param_3,&local_4c,param_3,param_4);
    goto switchD_00107762_default;
  case 2:
    __android_log_print(6,"BluetoothChatService","x2com_rcv - X2COM_ACK");
    puVar14 = PTR_0010cea8;
    if ((*PTR_0010ce48 == '\0') || (*PTR_0010cea8 == '\0')) goto switchD_00107762_default;
    iVar6 = x2com_parse_msg(param_3,&local_4c,param_3,param_4);
    bVar11 = *param_4;
    if ((bVar11 != 0) && (bVar18 = *PTR_0010cee8, (ulong)bVar18 != 0)) {
      bVar8 = 0xe;
      if (bVar11 < 0xe) {
        bVar8 = bVar11;
      }
      uVar15 = 0;
      bVar11 = 0;
      do {
        cVar1 = PTR_0010cef0[uVar15];
        uVar13 = 1;
        do {
          lVar10 = uVar13 - 1;
          if (bVar8 <= uVar13) break;
          uVar13 = uVar13 + 1;
        } while (cVar1 != param_3[lVar10]);
        if (cVar1 != param_3[lVar10]) {
          uVar13 = (ulong)bVar11;
          bVar11 = bVar11 + 1;
          local_46[uVar13] = cVar1;
        }
        uVar15 = uVar15 + 1;
      } while (uVar15 != bVar18);
      puVar16 = PTR_0010cef0;
      pbVar19 = PTR_0010cee8;
      if (bVar11 != 0) {
LAB_00107b0b:
        memcpy(puVar16,local_46,(ulong)bVar11);
        *pbVar19 = bVar11;
        goto switchD_00107762_default;
      }
    }
    *PTR_0010cee8 = 0;
    *puVar14 = 0;
    x2com_stop_ack_timer(param_1,param_2);
    if (*PTR_0010ceb0 == '\0') goto switchD_00107762_default;
    __android_log_print(6,"BluetoothChatService","x2com_rcv - X2COM_ACK_RCVD");
    *PTR_0010ce48 = 0;
    iVar6 = 7;
    cVar1 = *PTR_0010cea0;
    puVar7 = PTR_0010ceb8;
    goto joined_r0x00107b64;
  case 4:
    iVar6 = x2com_parse_msg(param_3,&local_4c,param_3,param_4);
    puVar14 = PTR_0010cf18;
    bVar11 = *param_4;
    if (bVar11 == 0) goto switchD_00107762_default;
    bVar18 = 0xe;
    if (bVar11 < 0xe) {
      bVar18 = bVar11;
    }
    if (bVar18 != 0) {
      uVar13 = (ulong)(byte)(bVar18 - 1);
      uVar15 = uVar13 + 1;
      if ((uVar15 < 0x20) ||
         ((PTR_0010cf18 < param_3 + uVar13 + 1 && (param_3 < PTR_0010cf18 + uVar13 + 1)))) {
        uVar9 = 0;
      }
      else {
        uVar9 = (uint)uVar15 & 0xffffffe0;
        uVar13 = (ulong)uVar9;
        lVar10 = (uVar13 - 0x20 >> 5) + 1;
        uVar12 = (ulong)((uint)lVar10 & 3);
        if (uVar13 - 0x20 < 0x60) {
          lVar17 = 0;
          puVar16 = PTR_0010cf18;
        }
        else {
          lVar10 = uVar12 - lVar10;
          lVar17 = 0;
          do {
            uVar2 = *(undefined8 *)((long)(param_3 + lVar17) + 8);
            uVar3 = *(undefined8 *)(param_3 + lVar17 + 0x10);
            uVar4 = *(undefined8 *)((long)(param_3 + lVar17 + 0x10) + 8);
            *(undefined8 *)(puVar14 + lVar17) = *(undefined8 *)(param_3 + lVar17);
            *(undefined8 *)((long)(puVar14 + lVar17) + 8) = uVar2;
            *(undefined8 *)(puVar14 + lVar17 + 0x10) = uVar3;
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x10) + 8) = uVar4;
            uVar2 = *(undefined8 *)((long)(param_3 + lVar17 + 0x20) + 8);
            uVar3 = *(undefined8 *)(param_3 + lVar17 + 0x30);
            uVar4 = *(undefined8 *)((long)(param_3 + lVar17 + 0x30) + 8);
            *(undefined8 *)(puVar14 + lVar17 + 0x20) = *(undefined8 *)(param_3 + lVar17 + 0x20);
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x20) + 8) = uVar2;
            *(undefined8 *)(puVar14 + lVar17 + 0x30) = uVar3;
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x30) + 8) = uVar4;
            uVar2 = *(undefined8 *)((long)(param_3 + lVar17 + 0x40) + 8);
            uVar3 = *(undefined8 *)(param_3 + lVar17 + 0x50);
            uVar4 = *(undefined8 *)((long)(param_3 + lVar17 + 0x50) + 8);
            *(undefined8 *)(puVar14 + lVar17 + 0x40) = *(undefined8 *)(param_3 + lVar17 + 0x40);
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x40) + 8) = uVar2;
            *(undefined8 *)(puVar14 + lVar17 + 0x50) = uVar3;
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x50) + 8) = uVar4;
            uVar2 = *(undefined8 *)((long)(param_3 + lVar17 + 0x60) + 8);
            uVar3 = *(undefined8 *)(param_3 + lVar17 + 0x70);
            uVar4 = *(undefined8 *)((long)(param_3 + lVar17 + 0x70) + 8);
            *(undefined8 *)(puVar14 + lVar17 + 0x60) = *(undefined8 *)(param_3 + lVar17 + 0x60);
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x60) + 8) = uVar2;
            *(undefined8 *)(puVar14 + lVar17 + 0x70) = uVar3;
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x70) + 8) = uVar4;
            lVar17 = lVar17 + 0x80;
            lVar10 = lVar10 + 4;
            puVar16 = PTR_0010cf18;
          } while (lVar10 != 0);
        }
        PTR_0010cf18 = puVar16;
        if (uVar12 != 0) {
          lVar17 = lVar17 + 0x10;
          lVar10 = -uVar12;
          do {
            uVar2 = *(undefined8 *)((long)(param_3 + lVar17 + -0x10) + 8);
            uVar3 = *(undefined8 *)(param_3 + lVar17);
            uVar4 = *(undefined8 *)((long)(param_3 + lVar17) + 8);
            *(undefined8 *)(puVar16 + lVar17 + -0x10) = *(undefined8 *)(param_3 + lVar17 + -0x10);
            *(undefined8 *)((long)(puVar16 + lVar17 + -0x10) + 8) = uVar2;
            *(undefined8 *)(puVar16 + lVar17) = uVar3;
            *(undefined8 *)((long)(puVar16 + lVar17) + 8) = uVar4;
            lVar17 = lVar17 + 0x20;
            lVar10 = lVar10 + 1;
          } while (lVar10 != 0);
        }
        if (uVar15 == uVar13) goto LAB_00107a43;
        param_3 = param_3 + uVar13;
        puVar14 = PTR_0010cf18 + uVar13;
      }
      lVar10 = 0;
      do {
        puVar14[lVar10] = param_3[lVar10];
        lVar10 = lVar10 + 1;
      } while ((byte)((char)uVar9 + (char)lVar10) < bVar18);
    }
LAB_00107a43:
    *PTR_0010cf20 = bVar18;
    puVar7 = PTR_0010cec0;
    break;
  case 5:
    if ((*PTR_0010ce68 == '\0') || (*PTR_0010ce88 == '\0')) goto switchD_00107762_default;
    iVar6 = x2com_parse_msg(param_3,&local_4c,param_3,param_4);
    bVar11 = *param_4;
    if ((bVar11 != 0) && (bVar18 = *PTR_0010cf08, (ulong)bVar18 != 0)) {
      bVar8 = 0xe;
      if (bVar11 < 0xe) {
        bVar8 = bVar11;
      }
      uVar15 = 0;
      bVar11 = 0;
      do {
        cVar1 = PTR_0010cf10[uVar15];
        uVar13 = 1;
        do {
          lVar10 = uVar13 - 1;
          if (bVar8 <= uVar13) break;
          uVar13 = uVar13 + 1;
        } while (cVar1 != param_3[lVar10]);
        if (cVar1 != param_3[lVar10]) {
          uVar13 = (ulong)bVar11;
          bVar11 = bVar11 + 1;
          local_46[uVar13] = cVar1;
        }
        uVar15 = uVar15 + 1;
      } while (uVar15 != bVar18);
      puVar16 = PTR_0010cf10;
      pbVar19 = PTR_0010cf08;
      if (bVar11 != 0) goto LAB_00107b0b;
    }
    *PTR_0010cf08 = 0;
    *PTR_0010ce88 = 0;
    x2com_stop_resp_timer(param_1,param_2);
    if (*PTR_0010ce90 == '\0') goto switchD_00107762_default;
    *puVar14 = 0;
    iVar6 = 6;
    cVar1 = *PTR_0010ce80;
    puVar7 = PTR_0010ce98;
joined_r0x00107b64:
    if (cVar1 == '\0') goto switchD_00107762_default;
    break;
  default:
    goto switchD_00107762_default;
  }
  *puVar7 = 1;
switchD_00107762_default:
  if (*(long *)(in_FS_OFFSET + 0x28) != local_38) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return iVar6;
}



// === x2com_set_msg_data at 00106240 (981 bytes) ===

byte x2com_set_msg_data(byte *param_1,int param_2,byte *param_3,char *param_4)

{
  byte bVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  ulong uVar5;
  char cVar6;
  undefined *puVar7;
  long lVar8;
  long lVar9;
  ulong uVar10;
  undefined8 *puVar11;
  byte *pbVar12;
  uint uVar13;
  byte *pbVar14;
  byte bVar15;
  char cVar16;
  byte bVar17;
  byte bVar18;
  ulong uVar19;
  byte *pbVar20;
  ulong uVar21;
  byte bVar22;
  long in_FS_OFFSET;
  byte local_46 [14];
  long local_38;
  
  local_38 = *(long *)(in_FS_OFFSET + 0x28);
  cVar16 = *param_4;
  uVar13 = 0;
  if (cVar16 == '\0') {
    cVar16 = '\0';
    bVar22 = 0;
  }
  else {
    uVar19 = 0;
    bVar22 = 0;
    puVar7 = PTR_one_byte_tx_p_0010cdf8;
    pbVar20 = param_3;
    do {
      bVar17 = *pbVar20;
      if ((param_2 == 4) || (param_2 == 2)) {
        *param_1 = bVar17;
        bVar22 = bVar22 + 1;
        param_1 = param_1 + 1;
      }
      else {
        uVar10 = (ulong)bVar17;
        if (bVar17 < 0x4b) {
          puVar11 = (undefined8 *)(puVar7 + uVar10 * 8);
        }
        else if (bVar17 < 0x96) {
          puVar11 = (undefined8 *)(PTR_two_byte_tx_p_0010ce00 + uVar10 * 8 + -600);
        }
        else if (bVar17 < 0xb9) {
          puVar11 = (undefined8 *)(PTR_three_byte_tx_p_0010ce08 + uVar10 * 8 + -0x4b0);
        }
        else if (bVar17 < 0xdc) {
          puVar11 = (undefined8 *)(PTR_four_byte_tx_p_0010ce10 + uVar10 * 8 + -0x5c8);
        }
        else {
          puVar11 = (undefined8 *)(PTR_var_byte_tx_p_0010ce18 + uVar10 * 8 + -0x6e0);
        }
        pbVar12 = (byte *)*puVar11;
        uVar10 = uVar19 & 0xff;
        if (pbVar12 != (byte *)0x0) {
          bVar15 = 1;
          if ((((0x4a < bVar17) && (bVar15 = 2, 0x95 < bVar17)) && (bVar15 = 3, 0xb8 < bVar17)) &&
             (bVar15 = *pbVar12, bVar17 < 0xdc)) {
            bVar15 = 4;
          }
          if (uVar13 + bVar15 < 0xe) {
            *param_1 = bVar17;
            pbVar14 = param_1 + 1;
            if (bVar15 == 0) {
              bVar22 = bVar22 + 1;
              param_1 = pbVar14;
              goto joined_r0x001065b5;
            }
            uVar5 = (ulong)(byte)(bVar15 - 1);
            uVar10 = uVar5 + 1;
            if (uVar10 < 0x20) {
              bVar17 = 0;
LAB_001064f6:
              bVar18 = ~bVar17;
              if ((bVar15 & 7) != 0) {
                cVar6 = '\0';
                do {
                  bVar1 = *pbVar12;
                  pbVar12 = pbVar12 + 1;
                  *pbVar14 = bVar1;
                  pbVar14 = pbVar14 + 1;
                  cVar6 = cVar6 + -1;
                } while (-(bVar15 & 7) != cVar6);
                bVar17 = bVar17 - cVar6;
                puVar7 = PTR_one_byte_tx_p_0010cdf8;
              }
              if (6 < (byte)(bVar18 + bVar15)) {
                lVar8 = 0;
                do {
                  pbVar14[lVar8] = pbVar12[lVar8];
                  pbVar14[lVar8 + 1] = pbVar12[lVar8 + 1];
                  pbVar14[lVar8 + 2] = pbVar12[lVar8 + 2];
                  pbVar14[lVar8 + 3] = pbVar12[lVar8 + 3];
                  pbVar14[lVar8 + 4] = pbVar12[lVar8 + 4];
                  pbVar14[lVar8 + 5] = pbVar12[lVar8 + 5];
                  pbVar14[lVar8 + 6] = pbVar12[lVar8 + 6];
                  pbVar14[lVar8 + 7] = pbVar12[lVar8 + 7];
                  lVar8 = lVar8 + 8;
                } while ((byte)(bVar15 - bVar17) != (char)lVar8);
                pbVar14 = pbVar14 + lVar8;
                puVar7 = PTR_one_byte_tx_p_0010cdf8;
              }
            }
            else {
              if ((pbVar14 < pbVar12 + uVar5 + 1) && (pbVar12 < param_1 + uVar5 + 2)) {
                uVar13 = 0;
LAB_001064ef:
                bVar17 = (byte)uVar13;
                puVar7 = PTR_one_byte_tx_p_0010cdf8;
                goto LAB_001064f6;
              }
              uVar13 = (uint)uVar10 & 0xffffffe0;
              uVar5 = (ulong)uVar13;
              lVar8 = (uVar5 - 0x20 >> 5) + 1;
              uVar21 = (ulong)((uint)lVar8 & 3);
              if (uVar5 - 0x20 < 0x60) {
                lVar9 = 0;
              }
              else {
                lVar8 = uVar21 - lVar8;
                lVar9 = 0;
                do {
                  uVar2 = *(undefined8 *)(pbVar12 + lVar9 + 8);
                  uVar3 = *(undefined8 *)(pbVar12 + lVar9 + 0x10);
                  uVar4 = *(undefined8 *)(pbVar12 + lVar9 + 0x10 + 8);
                  *(undefined8 *)(param_1 + lVar9 + 1) = *(undefined8 *)(pbVar12 + lVar9);
                  *(undefined8 *)(param_1 + lVar9 + 1 + 8) = uVar2;
                  *(undefined8 *)(param_1 + lVar9 + 0x11) = uVar3;
                  *(undefined8 *)(param_1 + lVar9 + 0x11 + 8) = uVar4;
                  uVar2 = *(undefined8 *)(pbVar12 + lVar9 + 0x20 + 8);
                  uVar3 = *(undefined8 *)(pbVar12 + lVar9 + 0x30);
                  uVar4 = *(undefined8 *)(pbVar12 + lVar9 + 0x30 + 8);
                  *(undefined8 *)(param_1 + lVar9 + 0x21) = *(undefined8 *)(pbVar12 + lVar9 + 0x20);
                  *(undefined8 *)(param_1 + lVar9 + 0x21 + 8) = uVar2;
                  *(undefined8 *)(param_1 + lVar9 + 0x31) = uVar3;
                  *(undefined8 *)(param_1 + lVar9 + 0x31 + 8) = uVar4;
                  uVar2 = *(undefined8 *)(pbVar12 + lVar9 + 0x40 + 8);
                  uVar3 = *(undefined8 *)(pbVar12 + lVar9 + 0x50);
                  uVar4 = *(undefined8 *)(pbVar12 + lVar9 + 0x50 + 8);
                  *(undefined8 *)(param_1 + lVar9 + 0x41) = *(undefined8 *)(pbVar12 + lVar9 + 0x40);
                  *(undefined8 *)(param_1 + lVar9 + 0x41 + 8) = uVar2;
                  *(undefined8 *)(param_1 + lVar9 + 0x51) = uVar3;
                  *(undefined8 *)(param_1 + lVar9 + 0x51 + 8) = uVar4;
                  uVar2 = *(undefined8 *)(pbVar12 + lVar9 + 0x60 + 8);
                  uVar3 = *(undefined8 *)(pbVar12 + lVar9 + 0x70);
                  uVar4 = *(undefined8 *)(pbVar12 + lVar9 + 0x70 + 8);
                  *(undefined8 *)(param_1 + lVar9 + 0x61) = *(undefined8 *)(pbVar12 + lVar9 + 0x60);
                  *(undefined8 *)(param_1 + lVar9 + 0x61 + 8) = uVar2;
                  *(undefined8 *)(param_1 + lVar9 + 0x71) = uVar3;
                  *(undefined8 *)(param_1 + lVar9 + 0x71 + 8) = uVar4;
                  lVar9 = lVar9 + 0x80;
                  lVar8 = lVar8 + 4;
                } while (lVar8 != 0);
              }
              if (uVar21 != 0) {
                lVar8 = 0;
                do {
                  uVar2 = *(undefined8 *)(pbVar12 + lVar8 + lVar9 + 8);
                  uVar3 = *(undefined8 *)(pbVar12 + lVar8 + lVar9 + 0x10);
                  uVar4 = *(undefined8 *)(pbVar12 + lVar8 + lVar9 + 0x10 + 8);
                  *(undefined8 *)(param_1 + lVar8 + lVar9 + 1) =
                       *(undefined8 *)(pbVar12 + lVar8 + lVar9);
                  *(undefined8 *)(param_1 + lVar8 + lVar9 + 1 + 8) = uVar2;
                  *(undefined8 *)(param_1 + lVar8 + lVar9 + 0x11) = uVar3;
                  *(undefined8 *)(param_1 + lVar8 + lVar9 + 0x11 + 8) = uVar4;
                  lVar8 = lVar8 + 0x20;
                } while (uVar21 << 5 != lVar8);
              }
              pbVar14 = pbVar14 + uVar5;
              puVar7 = PTR_one_byte_tx_p_0010cdf8;
              if (uVar10 != uVar5) {
                pbVar12 = pbVar12 + uVar5;
                goto LAB_001064ef;
              }
            }
            bVar22 = bVar22 + bVar15 + 1;
            param_1 = pbVar14;
            goto joined_r0x001065b5;
          }
        }
        uVar19 = (ulong)((int)uVar10 + 1);
        local_46[uVar10] = bVar17;
      }
joined_r0x001065b5:
      if (0xd < bVar22) break;
      cVar16 = cVar16 + -1;
      pbVar20 = pbVar20 + 1;
      uVar13 = (uint)bVar22;
    } while (cVar16 != '\0');
    cVar16 = (char)uVar19;
    if (cVar16 == '\0') {
      cVar16 = '\0';
    }
    else {
      memcpy(param_3,local_46,uVar19 & 0xff);
    }
  }
  *param_4 = cVar16;
  if (*(long *)(in_FS_OFFSET + 0x28) == local_38) {
    return bVar22;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



// === Java_com_quadzillapower_iQuad_bluetooth_BluetoothChatService_X2comCmd at 00106980 (489 bytes) ===

undefined8
Java_com_quadzillapower_iQuad_bluetooth_BluetoothChatService_X2comCmd
          (long *param_1,undefined8 param_2,undefined8 param_3,byte param_4)

{
  ulong uVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined8 uVar7;
  undefined8 uVar8;
  undefined8 uVar9;
  undefined *puVar10;
  ulong uVar11;
  undefined *puVar12;
  ulong uVar13;
  undefined *puVar14;
  long lVar15;
  long lVar16;
  byte bVar17;
  undefined8 uVar18;
  
  puVar10 = (undefined *)(**(code **)(*param_1 + 0x5c0))(param_1,param_3,0);
  if (puVar10 == (undefined *)0x0) {
    return 0;
  }
  uVar18 = 0;
  __android_log_print(3,"BluetoothChatService","X2comCmd");
  if (*PTR_0010ce28 != '\0' || *PTR_0010ce20 != '\0') goto LAB_00106a5d;
  *PTR_0010ce20 = 1;
  puVar12 = PTR_0010ce30;
  uVar18 = 1;
  if (param_4 == 0) goto LAB_00106a5d;
  bVar17 = 0xe;
  if (param_4 < 0xe) {
    bVar17 = param_4;
  }
  if (bVar17 != 0) {
    uVar11 = (ulong)(byte)(bVar17 - 1);
    uVar1 = uVar11 + 1;
    if ((uVar1 < 0x20) ||
       ((PTR_0010ce30 < puVar10 + uVar11 + 1 && (puVar10 < PTR_0010ce30 + uVar11 + 1)))) {
      uVar11 = 0;
      puVar12 = puVar10;
      puVar14 = PTR_0010ce30;
    }
    else {
      uVar11 = (ulong)((uint)uVar1 & 0xffffffe0);
      lVar15 = (uVar11 - 0x20 >> 5) + 1;
      uVar13 = (ulong)((uint)lVar15 & 3);
      if (uVar11 - 0x20 < 0x60) {
        lVar16 = 0;
        puVar14 = PTR_0010ce30;
      }
      else {
        lVar15 = uVar13 - lVar15;
        lVar16 = 0;
        do {
          uVar7 = *(undefined8 *)((long)(puVar10 + lVar16) + 8);
          uVar8 = *(undefined8 *)(puVar10 + lVar16 + 0x10);
          uVar9 = *(undefined8 *)((long)(puVar10 + lVar16 + 0x10) + 8);
          *(undefined8 *)(puVar12 + lVar16) = *(undefined8 *)(puVar10 + lVar16);
          *(undefined8 *)((long)(puVar12 + lVar16) + 8) = uVar7;
          *(undefined8 *)(puVar12 + lVar16 + 0x10) = uVar8;
          *(undefined8 *)((long)(puVar12 + lVar16 + 0x10) + 8) = uVar9;
          uVar7 = *(undefined8 *)((long)(puVar10 + lVar16 + 0x20) + 8);
          uVar8 = *(undefined8 *)(puVar10 + lVar16 + 0x30);
          uVar9 = *(undefined8 *)((long)(puVar10 + lVar16 + 0x30) + 8);
          *(undefined8 *)(puVar12 + lVar16 + 0x20) = *(undefined8 *)(puVar10 + lVar16 + 0x20);
          *(undefined8 *)((long)(puVar12 + lVar16 + 0x20) + 8) = uVar7;
          *(undefined8 *)(puVar12 + lVar16 + 0x30) = uVar8;
          *(undefined8 *)((long)(puVar12 + lVar16 + 0x30) + 8) = uVar9;
          uVar7 = *(undefined8 *)((long)(puVar10 + lVar16 + 0x40) + 8);
          uVar8 = *(undefined8 *)(puVar10 + lVar16 + 0x50);
          uVar9 = *(undefined8 *)((long)(puVar10 + lVar16 + 0x50) + 8);
          *(undefined8 *)(puVar12 + lVar16 + 0x40) = *(undefined8 *)(puVar10 + lVar16 + 0x40);
          *(undefined8 *)((long)(puVar12 + lVar16 + 0x40) + 8) = uVar7;
          *(undefined8 *)(puVar12 + lVar16 + 0x50) = uVar8;
          *(undefined8 *)((long)(puVar12 + lVar16 + 0x50) + 8) = uVar9;
          puVar2 = (undefined4 *)(puVar10 + lVar16 + 0x60);
          uVar4 = puVar2[1];
          uVar5 = puVar2[2];
          uVar6 = puVar2[3];
          uVar7 = *(undefined8 *)(puVar10 + lVar16 + 0x70);
          uVar8 = *(undefined8 *)((long)(puVar10 + lVar16 + 0x70) + 8);
          puVar3 = (undefined4 *)(puVar12 + lVar16 + 0x60);
          *puVar3 = *puVar2;
          puVar3[1] = uVar4;
          puVar3[2] = uVar5;
          puVar3[3] = uVar6;
          *(undefined8 *)(puVar12 + lVar16 + 0x70) = uVar7;
          *(undefined8 *)((long)(puVar12 + lVar16 + 0x70) + 8) = uVar8;
          lVar16 = lVar16 + 0x80;
          lVar15 = lVar15 + 4;
          puVar14 = PTR_0010ce30;
        } while (lVar15 != 0);
      }
      PTR_0010ce30 = puVar14;
      if (uVar13 != 0) {
        lVar16 = lVar16 + 0x10;
        lVar15 = -uVar13;
        do {
          puVar2 = (undefined4 *)(puVar10 + lVar16 + -0x10);
          uVar4 = puVar2[1];
          uVar5 = puVar2[2];
          uVar6 = puVar2[3];
          uVar7 = *(undefined8 *)(puVar10 + lVar16);
          uVar8 = *(undefined8 *)((long)(puVar10 + lVar16) + 8);
          puVar3 = (undefined4 *)(puVar14 + lVar16 + -0x10);
          *puVar3 = *puVar2;
          puVar3[1] = uVar4;
          puVar3[2] = uVar5;
          puVar3[3] = uVar6;
          *(undefined8 *)(puVar14 + lVar16) = uVar7;
          *(undefined8 *)((long)(puVar14 + lVar16) + 8) = uVar8;
          lVar16 = lVar16 + 0x20;
          lVar15 = lVar15 + 1;
        } while (lVar15 != 0);
      }
      if (uVar1 == uVar11) goto LAB_00106a53;
      puVar12 = puVar10 + uVar11;
      puVar14 = PTR_0010ce30 + uVar11;
    }
    lVar15 = 0;
    do {
      puVar14[lVar15] = puVar12[lVar15];
      lVar15 = lVar15 + 1;
    } while ((byte)((char)uVar11 + (char)lVar15) < bVar17);
  }
LAB_00106a53:
  *PTR_0010ce38 = bVar17;
LAB_00106a5d:
  (**(code **)(*param_1 + 0x600))(param_1,param_3,puVar10,0);
  return uVar18;
}



// === Java_com_quadzillapower_iQuad_bluetooth_BluetoothChatService_X2comCwa at 00106d10 (489 bytes) ===

undefined8
Java_com_quadzillapower_iQuad_bluetooth_BluetoothChatService_X2comCwa
          (long *param_1,undefined8 param_2,undefined8 param_3,byte param_4)

{
  ulong uVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined8 uVar7;
  undefined8 uVar8;
  undefined8 uVar9;
  undefined *puVar10;
  ulong uVar11;
  undefined *puVar12;
  ulong uVar13;
  undefined *puVar14;
  long lVar15;
  long lVar16;
  byte bVar17;
  undefined8 uVar18;
  
  puVar10 = (undefined *)(**(code **)(*param_1 + 0x5c0))(param_1,param_3,0);
  if (puVar10 == (undefined *)0x0) {
    return 0;
  }
  uVar18 = 0;
  __android_log_print(3,"BluetoothChatService","X2comCwa");
  if (*PTR_0010ce48 != '\0' || *PTR_0010ce40 != '\0') goto LAB_00106ded;
  *PTR_0010ce40 = 1;
  puVar12 = PTR_0010ce50;
  uVar18 = 1;
  if (param_4 == 0) goto LAB_00106ded;
  bVar17 = 0xe;
  if (param_4 < 0xe) {
    bVar17 = param_4;
  }
  if (bVar17 != 0) {
    uVar11 = (ulong)(byte)(bVar17 - 1);
    uVar1 = uVar11 + 1;
    if ((uVar1 < 0x20) ||
       ((PTR_0010ce50 < puVar10 + uVar11 + 1 && (puVar10 < PTR_0010ce50 + uVar11 + 1)))) {
      uVar11 = 0;
      puVar12 = puVar10;
      puVar14 = PTR_0010ce50;
    }
    else {
      uVar11 = (ulong)((uint)uVar1 & 0xffffffe0);
      lVar15 = (uVar11 - 0x20 >> 5) + 1;
      uVar13 = (ulong)((uint)lVar15 & 3);
      if (uVar11 - 0x20 < 0x60) {
        lVar16 = 0;
        puVar14 = PTR_0010ce50;
      }
      else {
        lVar15 = uVar13 - lVar15;
        lVar16 = 0;
        do {
          uVar7 = *(undefined8 *)((long)(puVar10 + lVar16) + 8);
          uVar8 = *(undefined8 *)(puVar10 + lVar16 + 0x10);
          uVar9 = *(undefined8 *)((long)(puVar10 + lVar16 + 0x10) + 8);
          *(undefined8 *)(puVar12 + lVar16) = *(undefined8 *)(puVar10 + lVar16);
          *(undefined8 *)((long)(puVar12 + lVar16) + 8) = uVar7;
          *(undefined8 *)(puVar12 + lVar16 + 0x10) = uVar8;
          *(undefined8 *)((long)(puVar12 + lVar16 + 0x10) + 8) = uVar9;
          uVar7 = *(undefined8 *)((long)(puVar10 + lVar16 + 0x20) + 8);
          uVar8 = *(undefined8 *)(puVar10 + lVar16 + 0x30);
          uVar9 = *(undefined8 *)((long)(puVar10 + lVar16 + 0x30) + 8);
          *(undefined8 *)(puVar12 + lVar16 + 0x20) = *(undefined8 *)(puVar10 + lVar16 + 0x20);
          *(undefined8 *)((long)(puVar12 + lVar16 + 0x20) + 8) = uVar7;
          *(undefined8 *)(puVar12 + lVar16 + 0x30) = uVar8;
          *(undefined8 *)((long)(puVar12 + lVar16 + 0x30) + 8) = uVar9;
          uVar7 = *(undefined8 *)((long)(puVar10 + lVar16 + 0x40) + 8);
          uVar8 = *(undefined8 *)(puVar10 + lVar16 + 0x50);
          uVar9 = *(undefined8 *)((long)(puVar10 + lVar16 + 0x50) + 8);
          *(undefined8 *)(puVar12 + lVar16 + 0x40) = *(undefined8 *)(puVar10 + lVar16 + 0x40);
          *(undefined8 *)((long)(puVar12 + lVar16 + 0x40) + 8) = uVar7;
          *(undefined8 *)(puVar12 + lVar16 + 0x50) = uVar8;
          *(undefined8 *)((long)(puVar12 + lVar16 + 0x50) + 8) = uVar9;
          puVar2 = (undefined4 *)(puVar10 + lVar16 + 0x60);
          uVar4 = puVar2[1];
          uVar5 = puVar2[2];
          uVar6 = puVar2[3];
          uVar7 = *(undefined8 *)(puVar10 + lVar16 + 0x70);
          uVar8 = *(undefined8 *)((long)(puVar10 + lVar16 + 0x70) + 8);
          puVar3 = (undefined4 *)(puVar12 + lVar16 + 0x60);
          *puVar3 = *puVar2;
          puVar3[1] = uVar4;
          puVar3[2] = uVar5;
          puVar3[3] = uVar6;
          *(undefined8 *)(puVar12 + lVar16 + 0x70) = uVar7;
          *(undefined8 *)((long)(puVar12 + lVar16 + 0x70) + 8) = uVar8;
          lVar16 = lVar16 + 0x80;
          lVar15 = lVar15 + 4;
          puVar14 = PTR_0010ce50;
        } while (lVar15 != 0);
      }
      PTR_0010ce50 = puVar14;
      if (uVar13 != 0) {
        lVar16 = lVar16 + 0x10;
        lVar15 = -uVar13;
        do {
          puVar2 = (undefined4 *)(puVar10 + lVar16 + -0x10);
          uVar4 = puVar2[1];
          uVar5 = puVar2[2];
          uVar6 = puVar2[3];
          uVar7 = *(undefined8 *)(puVar10 + lVar16);
          uVar8 = *(undefined8 *)((long)(puVar10 + lVar16) + 8);
          puVar3 = (undefined4 *)(puVar14 + lVar16 + -0x10);
          *puVar3 = *puVar2;
          puVar3[1] = uVar4;
          puVar3[2] = uVar5;
          puVar3[3] = uVar6;
          *(undefined8 *)(puVar14 + lVar16) = uVar7;
          *(undefined8 *)((long)(puVar14 + lVar16) + 8) = uVar8;
          lVar16 = lVar16 + 0x20;
          lVar15 = lVar15 + 1;
        } while (lVar15 != 0);
      }
      if (uVar1 == uVar11) goto LAB_00106de3;
      puVar12 = puVar10 + uVar11;
      puVar14 = PTR_0010ce50 + uVar11;
    }
    lVar15 = 0;
    do {
      puVar14[lVar15] = puVar12[lVar15];
      lVar15 = lVar15 + 1;
    } while ((byte)((char)uVar11 + (char)lVar15) < bVar17);
  }
LAB_00106de3:
  *PTR_0010ce58 = bVar17;
LAB_00106ded:
  (**(code **)(*param_1 + 0x600))(param_1,param_3,puVar10,0);
  return uVar18;
}



// === Java_com_quadzillapower_iQuad_bluetooth_BluetoothChatService_X2comReq at 001070a0 (473 bytes) ===

undefined8
Java_com_quadzillapower_iQuad_bluetooth_BluetoothChatService_X2comReq
          (long *param_1,undefined8 param_2,undefined8 param_3,byte param_4)

{
  ulong uVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined8 uVar7;
  undefined8 uVar8;
  undefined8 uVar9;
  undefined *puVar10;
  ulong uVar11;
  long lVar12;
  long lVar13;
  undefined *puVar14;
  undefined *puVar15;
  uint uVar16;
  byte bVar18;
  undefined8 uVar19;
  ulong uVar17;
  
  puVar10 = (undefined *)(**(code **)(*param_1 + 0x5c0))(param_1,param_3,0);
  if (puVar10 == (undefined *)0x0) {
    return 0;
  }
  if (*PTR_0010ce68 != '\0' || *PTR_0010ce60 != '\0') {
    uVar19 = 0;
    goto LAB_0010716d;
  }
  *PTR_0010ce60 = 1;
  puVar14 = PTR_0010ce70;
  uVar19 = 1;
  if (param_4 == 0) goto LAB_0010716d;
  bVar18 = 0xe;
  if (param_4 < 0xe) {
    bVar18 = param_4;
  }
  if (bVar18 != 0) {
    uVar11 = (ulong)(byte)(bVar18 - 1);
    uVar1 = uVar11 + 1;
    if ((uVar1 < 0x20) ||
       ((PTR_0010ce70 < puVar10 + uVar11 + 1 && (puVar10 < PTR_0010ce70 + uVar11 + 1)))) {
      uVar16 = 0;
      puVar14 = puVar10;
      puVar15 = PTR_0010ce70;
    }
    else {
      uVar16 = (uint)uVar1 & 0xffffffe0;
      uVar17 = (ulong)uVar16;
      lVar12 = (uVar17 - 0x20 >> 5) + 1;
      uVar11 = (ulong)((uint)lVar12 & 3);
      if (uVar17 - 0x20 < 0x60) {
        lVar13 = 0;
        puVar15 = PTR_0010ce70;
      }
      else {
        lVar12 = uVar11 - lVar12;
        lVar13 = 0;
        do {
          uVar7 = *(undefined8 *)((long)(puVar10 + lVar13) + 8);
          uVar8 = *(undefined8 *)(puVar10 + lVar13 + 0x10);
          uVar9 = *(undefined8 *)((long)(puVar10 + lVar13 + 0x10) + 8);
          *(undefined8 *)(puVar14 + lVar13) = *(undefined8 *)(puVar10 + lVar13);
          *(undefined8 *)((long)(puVar14 + lVar13) + 8) = uVar7;
          *(undefined8 *)(puVar14 + lVar13 + 0x10) = uVar8;
          *(undefined8 *)((long)(puVar14 + lVar13 + 0x10) + 8) = uVar9;
          uVar7 = *(undefined8 *)((long)(puVar10 + lVar13 + 0x20) + 8);
          uVar8 = *(undefined8 *)(puVar10 + lVar13 + 0x30);
          uVar9 = *(undefined8 *)((long)(puVar10 + lVar13 + 0x30) + 8);
          *(undefined8 *)(puVar14 + lVar13 + 0x20) = *(undefined8 *)(puVar10 + lVar13 + 0x20);
          *(undefined8 *)((long)(puVar14 + lVar13 + 0x20) + 8) = uVar7;
          *(undefined8 *)(puVar14 + lVar13 + 0x30) = uVar8;
          *(undefined8 *)((long)(puVar14 + lVar13 + 0x30) + 8) = uVar9;
          uVar7 = *(undefined8 *)((long)(puVar10 + lVar13 + 0x40) + 8);
          uVar8 = *(undefined8 *)(puVar10 + lVar13 + 0x50);
          uVar9 = *(undefined8 *)((long)(puVar10 + lVar13 + 0x50) + 8);
          *(undefined8 *)(puVar14 + lVar13 + 0x40) = *(undefined8 *)(puVar10 + lVar13 + 0x40);
          *(undefined8 *)((long)(puVar14 + lVar13 + 0x40) + 8) = uVar7;
          *(undefined8 *)(puVar14 + lVar13 + 0x50) = uVar8;
          *(undefined8 *)((long)(puVar14 + lVar13 + 0x50) + 8) = uVar9;
          puVar2 = (undefined4 *)(puVar10 + lVar13 + 0x60);
          uVar4 = puVar2[1];
          uVar5 = puVar2[2];
          uVar6 = puVar2[3];
          uVar7 = *(undefined8 *)(puVar10 + lVar13 + 0x70);
          uVar8 = *(undefined8 *)((long)(puVar10 + lVar13 + 0x70) + 8);
          puVar3 = (undefined4 *)(puVar14 + lVar13 + 0x60);
          *puVar3 = *puVar2;
          puVar3[1] = uVar4;
          puVar3[2] = uVar5;
          puVar3[3] = uVar6;
          *(undefined8 *)(puVar14 + lVar13 + 0x70) = uVar7;
          *(undefined8 *)((long)(puVar14 + lVar13 + 0x70) + 8) = uVar8;
          lVar13 = lVar13 + 0x80;
          lVar12 = lVar12 + 4;
          puVar15 = PTR_0010ce70;
        } while (lVar12 != 0);
      }
      PTR_0010ce70 = puVar15;
      if (uVar11 != 0) {
        lVar13 = lVar13 + 0x10;
        lVar12 = -uVar11;
        do {
          puVar2 = (undefined4 *)(puVar10 + lVar13 + -0x10);
          uVar4 = puVar2[1];
          uVar5 = puVar2[2];
          uVar6 = puVar2[3];
          uVar7 = *(undefined8 *)(puVar10 + lVar13);
          uVar8 = *(undefined8 *)((long)(puVar10 + lVar13) + 8);
          puVar3 = (undefined4 *)(puVar15 + lVar13 + -0x10);
          *puVar3 = *puVar2;
          puVar3[1] = uVar4;
          puVar3[2] = uVar5;
          puVar3[3] = uVar6;
          *(undefined8 *)(puVar15 + lVar13) = uVar7;
          *(undefined8 *)((long)(puVar15 + lVar13) + 8) = uVar8;
          lVar13 = lVar13 + 0x20;
          lVar12 = lVar12 + 1;
        } while (lVar12 != 0);
      }
      if (uVar1 == uVar17) goto LAB_00107163;
      puVar14 = puVar10 + uVar17;
      puVar15 = PTR_0010ce70 + uVar17;
    }
    lVar12 = 0;
    do {
      puVar15[lVar12] = puVar14[lVar12];
      lVar12 = lVar12 + 1;
    } while ((byte)((char)uVar16 + (char)lVar12) < bVar18);
  }
LAB_00107163:
  *PTR_0010ce78 = bVar18;
LAB_0010716d:
  (**(code **)(*param_1 + 0x600))(param_1,param_3,puVar10,0);
  return uVar19;
}



// === x2com_enable_rx at 001059b0 (432 bytes) ===

void x2com_enable_rx(long *param_1,undefined8 param_2,undefined1 *param_3)

{
  undefined *puVar1;
  long lVar2;
  long lVar3;
  undefined1 *puVar4;
  
  lVar2 = (**(code **)(*param_1 + 0x30))
                    (param_1,"com/quadzillapower/iQuad/bluetooth/BluetoothChatService");
  if (lVar2 != 0) {
    lVar3 = (**(code **)(*param_1 + 0x108))(param_1,lVar2,"getNextByte",&DAT_00109462);
    if (lVar3 != 0) {
      lVar3 = (**(code **)(*param_1 + 0x110))(param_1,param_2,lVar3);
      if (lVar3 != 0) {
        puVar4 = (undefined1 *)(**(code **)(*param_1 + 0x5c0))(param_1,lVar3,0);
        puVar1 = PTR_0010cdc8;
        *(undefined1 **)PTR_0010cdc8 = puVar4 + 1;
        *param_3 = *puVar4;
        puVar4 = *(undefined1 **)puVar1;
        *(undefined1 **)puVar1 = puVar4 + 1;
        param_3[1] = *puVar4;
        puVar4 = *(undefined1 **)puVar1;
        *(undefined1 **)puVar1 = puVar4 + 1;
        param_3[2] = *puVar4;
        puVar4 = *(undefined1 **)puVar1;
        *(undefined1 **)puVar1 = puVar4 + 1;
        param_3[3] = *puVar4;
        puVar4 = *(undefined1 **)puVar1;
        *(undefined1 **)puVar1 = puVar4 + 1;
        param_3[4] = *puVar4;
        puVar4 = *(undefined1 **)puVar1;
        *(undefined1 **)puVar1 = puVar4 + 1;
        param_3[5] = *puVar4;
        puVar4 = *(undefined1 **)puVar1;
        *(undefined1 **)puVar1 = puVar4 + 1;
        param_3[6] = *puVar4;
        puVar4 = *(undefined1 **)puVar1;
        *(undefined1 **)puVar1 = puVar4 + 1;
        param_3[7] = *puVar4;
        puVar4 = *(undefined1 **)puVar1;
        *(undefined1 **)puVar1 = puVar4 + 1;
        param_3[8] = *puVar4;
        *(undefined1 **)puVar1 = puVar4 + 2;
        param_3[9] = puVar4[1];
        *(undefined1 **)puVar1 = puVar4 + 3;
        param_3[10] = puVar4[2];
        *(undefined1 **)puVar1 = puVar4 + 4;
        param_3[0xb] = puVar4[3];
        *(undefined1 **)puVar1 = puVar4 + 5;
        param_3[0xc] = puVar4[4];
        *(undefined1 **)puVar1 = puVar4 + 6;
        param_3[0xd] = puVar4[5];
        *(undefined1 **)puVar1 = puVar4 + 7;
        param_3[0xe] = puVar4[6];
        *(undefined1 **)puVar1 = puVar4 + 8;
        param_3[0xf] = puVar4[7];
        (**(code **)(*param_1 + 0x600))(param_1,lVar3,puVar4 + 8,0);
      }
                    /* WARNING: Could not recover jumptable at 0x00105b52. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      (**(code **)(*param_1 + 0xb8))(param_1,lVar2);
      return;
    }
  }
  return;
}



// === x2com_generate_crc at 00105d60 (429 bytes) ===

byte x2com_generate_crc(long param_1,char param_2)

{
  byte bVar1;
  byte bVar2;
  byte bVar3;
  long lVar4;
  
  if (param_2 == '\0') {
    return 0;
  }
  bVar3 = 0xff;
  lVar4 = 0;
  do {
    bVar1 = *(byte *)(param_1 + lVar4);
    if ((char)bVar1 < '\0') {
      bVar2 = 0x1c;
      if ((char)bVar3 < '\0') {
        bVar2 = 1;
      }
      bVar2 = (bVar3 * '\x02' | 1) ^ bVar2;
      if ((bVar1 & 0x40) == 0) goto LAB_00105dbb;
LAB_00105e7b:
      bVar3 = 0x1c;
      if ((char)bVar2 < '\0') {
        bVar3 = 1;
      }
      bVar3 = (bVar2 * '\x02' | 1) ^ bVar3;
      if ((bVar1 & 0x20) != 0) goto LAB_00105dd0;
LAB_00105e95:
      bVar2 = bVar3 * '\x02' ^ (char)bVar3 >> 7 & 0x1dU;
      if ((bVar1 & 0x10) != 0) goto LAB_00105dea;
LAB_00105eaa:
      bVar3 = bVar2 * '\x02' ^ (char)bVar2 >> 7 & 0x1dU;
      if ((bVar1 & 8) != 0) goto LAB_00105e04;
LAB_00105ebf:
      bVar2 = bVar3 * '\x02' ^ (char)bVar3 >> 7 & 0x1dU;
      if ((bVar1 & 4) != 0) goto LAB_00105e1e;
LAB_00105ed4:
      bVar3 = bVar2 * '\x02' ^ (char)bVar2 >> 7 & 0x1dU;
      if ((bVar1 & 2) != 0) goto LAB_00105e38;
LAB_00105ee9:
      bVar2 = bVar3 * '\x02' ^ (char)bVar3 >> 7 & 0x1dU;
      if ((bVar1 & 1) != 0) goto LAB_00105efe;
LAB_00105d80:
      bVar3 = bVar2 * '\x02' ^ (char)bVar2 >> 7 & 0x1dU;
    }
    else {
      bVar2 = bVar3 * '\x02' ^ (char)bVar3 >> 7 & 0x1dU;
      if ((bVar1 & 0x40) != 0) goto LAB_00105e7b;
LAB_00105dbb:
      bVar3 = bVar2 * '\x02' ^ (char)bVar2 >> 7 & 0x1dU;
      if ((bVar1 & 0x20) == 0) goto LAB_00105e95;
LAB_00105dd0:
      bVar2 = 0x1c;
      if ((char)bVar3 < '\0') {
        bVar2 = 1;
      }
      bVar2 = (bVar3 * '\x02' | 1) ^ bVar2;
      if ((bVar1 & 0x10) == 0) goto LAB_00105eaa;
LAB_00105dea:
      bVar3 = 0x1c;
      if ((char)bVar2 < '\0') {
        bVar3 = 1;
      }
      bVar3 = (bVar2 * '\x02' | 1) ^ bVar3;
      if ((bVar1 & 8) == 0) goto LAB_00105ebf;
LAB_00105e04:
      bVar2 = 0x1c;
      if ((char)bVar3 < '\0') {
        bVar2 = 1;
      }
      bVar2 = (bVar3 * '\x02' | 1) ^ bVar2;
      if ((bVar1 & 4) == 0) goto LAB_00105ed4;
LAB_00105e1e:
      bVar3 = 0x1c;
      if ((char)bVar2 < '\0') {
        bVar3 = 1;
      }
      bVar3 = (bVar2 * '\x02' | 1) ^ bVar3;
      if ((bVar1 & 2) == 0) goto LAB_00105ee9;
LAB_00105e38:
      bVar2 = 0x1c;
      if ((char)bVar3 < '\0') {
        bVar2 = 1;
      }
      bVar2 = (bVar3 * '\x02' | 1) ^ bVar2;
      if ((bVar1 & 1) == 0) goto LAB_00105d80;
LAB_00105efe:
      bVar3 = 0x1c;
      if ((char)bVar2 < '\0') {
        bVar3 = 1;
      }
      bVar3 = (bVar2 * '\x02' | 1) ^ bVar3;
    }
    lVar4 = lVar4 + 1;
    if (param_2 == (char)lVar4) {
      return ~bVar3;
    }
  } while( true );
}



// === x2com_cmd at 00106b70 (406 bytes) ===

undefined8 x2com_cmd(undefined *param_1,byte param_2)

{
  ulong uVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined *puVar5;
  undefined8 uVar6;
  ulong uVar7;
  long lVar8;
  long lVar9;
  uint uVar10;
  byte bVar12;
  undefined *puVar13;
  ulong uVar11;
  
  puVar13 = PTR_0010ce20;
  if (*PTR_0010ce28 != '\0' || *PTR_0010ce20 != '\0') {
    return 0;
  }
  *PTR_0010ce20 = 1;
  puVar5 = PTR_0010ce30;
  uVar6 = CONCAT71((int7)((ulong)puVar13 >> 8),1);
  if (param_2 == 0) {
    return uVar6;
  }
  bVar12 = 0xe;
  if (param_2 < 0xe) {
    bVar12 = param_2;
  }
  if (bVar12 != 0) {
    uVar7 = (ulong)(byte)(bVar12 - 1);
    uVar1 = uVar7 + 1;
    if ((uVar1 < 0x20) ||
       ((PTR_0010ce30 < param_1 + uVar7 + 1 && (param_1 < PTR_0010ce30 + uVar7 + 1)))) {
      uVar10 = 0;
      puVar13 = PTR_0010ce30;
    }
    else {
      uVar10 = (uint)uVar1 & 0xffffffe0;
      uVar11 = (ulong)uVar10;
      lVar9 = (uVar11 - 0x20 >> 5) + 1;
      uVar7 = (ulong)((uint)lVar9 & 3);
      if (uVar11 - 0x20 < 0x60) {
        lVar8 = 0;
        puVar13 = PTR_0010ce30;
      }
      else {
        lVar9 = uVar7 - lVar9;
        lVar8 = 0;
        do {
          uVar2 = *(undefined8 *)((long)(param_1 + lVar8) + 8);
          uVar3 = *(undefined8 *)(param_1 + lVar8 + 0x10);
          uVar4 = *(undefined8 *)((long)(param_1 + lVar8 + 0x10) + 8);
          *(undefined8 *)(puVar5 + lVar8) = *(undefined8 *)(param_1 + lVar8);
          *(undefined8 *)((long)(puVar5 + lVar8) + 8) = uVar2;
          *(undefined8 *)(puVar5 + lVar8 + 0x10) = uVar3;
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x10) + 8) = uVar4;
          uVar2 = *(undefined8 *)((long)(param_1 + lVar8 + 0x20) + 8);
          uVar3 = *(undefined8 *)(param_1 + lVar8 + 0x30);
          uVar4 = *(undefined8 *)((long)(param_1 + lVar8 + 0x30) + 8);
          *(undefined8 *)(puVar5 + lVar8 + 0x20) = *(undefined8 *)(param_1 + lVar8 + 0x20);
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x20) + 8) = uVar2;
          *(undefined8 *)(puVar5 + lVar8 + 0x30) = uVar3;
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x30) + 8) = uVar4;
          uVar2 = *(undefined8 *)((long)(param_1 + lVar8 + 0x40) + 8);
          uVar3 = *(undefined8 *)(param_1 + lVar8 + 0x50);
          uVar4 = *(undefined8 *)((long)(param_1 + lVar8 + 0x50) + 8);
          *(undefined8 *)(puVar5 + lVar8 + 0x40) = *(undefined8 *)(param_1 + lVar8 + 0x40);
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x40) + 8) = uVar2;
          *(undefined8 *)(puVar5 + lVar8 + 0x50) = uVar3;
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x50) + 8) = uVar4;
          uVar2 = *(undefined8 *)((long)(param_1 + lVar8 + 0x60) + 8);
          uVar3 = *(undefined8 *)(param_1 + lVar8 + 0x70);
          uVar4 = *(undefined8 *)((long)(param_1 + lVar8 + 0x70) + 8);
          *(undefined8 *)(puVar5 + lVar8 + 0x60) = *(undefined8 *)(param_1 + lVar8 + 0x60);
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x60) + 8) = uVar2;
          *(undefined8 *)(puVar5 + lVar8 + 0x70) = uVar3;
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x70) + 8) = uVar4;
          lVar8 = lVar8 + 0x80;
          lVar9 = lVar9 + 4;
          puVar13 = PTR_0010ce30;
        } while (lVar9 != 0);
      }
      PTR_0010ce30 = puVar13;
      if (uVar7 != 0) {
        lVar8 = lVar8 + 0x10;
        lVar9 = -uVar7;
        do {
          uVar2 = *(undefined8 *)((long)(param_1 + lVar8 + -0x10) + 8);
          uVar3 = *(undefined8 *)(param_1 + lVar8);
          uVar4 = *(undefined8 *)((long)(param_1 + lVar8) + 8);
          *(undefined8 *)(puVar13 + lVar8 + -0x10) = *(undefined8 *)(param_1 + lVar8 + -0x10);
          *(undefined8 *)((long)(puVar13 + lVar8 + -0x10) + 8) = uVar2;
          *(undefined8 *)(puVar13 + lVar8) = uVar3;
          *(undefined8 *)((long)(puVar13 + lVar8) + 8) = uVar4;
          lVar8 = lVar8 + 0x20;
          lVar9 = lVar9 + 1;
        } while (lVar9 != 0);
      }
      if (uVar1 == uVar11) goto LAB_00106c04;
      param_1 = param_1 + uVar11;
      puVar13 = PTR_0010ce30 + uVar11;
    }
    lVar9 = 0;
    do {
      puVar13[lVar9] = param_1[lVar9];
      lVar9 = lVar9 + 1;
    } while ((byte)((char)uVar10 + (char)lVar9) < bVar12);
  }
LAB_00106c04:
  *PTR_0010ce38 = bVar12;
  return uVar6;
}



// === x2com_cwa at 00106f00 (406 bytes) ===

undefined8 x2com_cwa(undefined *param_1,byte param_2)

{
  ulong uVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined *puVar5;
  undefined8 uVar6;
  ulong uVar7;
  long lVar8;
  long lVar9;
  uint uVar10;
  byte bVar12;
  undefined *puVar13;
  ulong uVar11;
  
  puVar13 = PTR_0010ce40;
  if (*PTR_0010ce48 != '\0' || *PTR_0010ce40 != '\0') {
    return 0;
  }
  *PTR_0010ce40 = 1;
  puVar5 = PTR_0010ce50;
  uVar6 = CONCAT71((int7)((ulong)puVar13 >> 8),1);
  if (param_2 == 0) {
    return uVar6;
  }
  bVar12 = 0xe;
  if (param_2 < 0xe) {
    bVar12 = param_2;
  }
  if (bVar12 != 0) {
    uVar7 = (ulong)(byte)(bVar12 - 1);
    uVar1 = uVar7 + 1;
    if ((uVar1 < 0x20) ||
       ((PTR_0010ce50 < param_1 + uVar7 + 1 && (param_1 < PTR_0010ce50 + uVar7 + 1)))) {
      uVar10 = 0;
      puVar13 = PTR_0010ce50;
    }
    else {
      uVar10 = (uint)uVar1 & 0xffffffe0;
      uVar11 = (ulong)uVar10;
      lVar9 = (uVar11 - 0x20 >> 5) + 1;
      uVar7 = (ulong)((uint)lVar9 & 3);
      if (uVar11 - 0x20 < 0x60) {
        lVar8 = 0;
        puVar13 = PTR_0010ce50;
      }
      else {
        lVar9 = uVar7 - lVar9;
        lVar8 = 0;
        do {
          uVar2 = *(undefined8 *)((long)(param_1 + lVar8) + 8);
          uVar3 = *(undefined8 *)(param_1 + lVar8 + 0x10);
          uVar4 = *(undefined8 *)((long)(param_1 + lVar8 + 0x10) + 8);
          *(undefined8 *)(puVar5 + lVar8) = *(undefined8 *)(param_1 + lVar8);
          *(undefined8 *)((long)(puVar5 + lVar8) + 8) = uVar2;
          *(undefined8 *)(puVar5 + lVar8 + 0x10) = uVar3;
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x10) + 8) = uVar4;
          uVar2 = *(undefined8 *)((long)(param_1 + lVar8 + 0x20) + 8);
          uVar3 = *(undefined8 *)(param_1 + lVar8 + 0x30);
          uVar4 = *(undefined8 *)((long)(param_1 + lVar8 + 0x30) + 8);
          *(undefined8 *)(puVar5 + lVar8 + 0x20) = *(undefined8 *)(param_1 + lVar8 + 0x20);
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x20) + 8) = uVar2;
          *(undefined8 *)(puVar5 + lVar8 + 0x30) = uVar3;
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x30) + 8) = uVar4;
          uVar2 = *(undefined8 *)((long)(param_1 + lVar8 + 0x40) + 8);
          uVar3 = *(undefined8 *)(param_1 + lVar8 + 0x50);
          uVar4 = *(undefined8 *)((long)(param_1 + lVar8 + 0x50) + 8);
          *(undefined8 *)(puVar5 + lVar8 + 0x40) = *(undefined8 *)(param_1 + lVar8 + 0x40);
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x40) + 8) = uVar2;
          *(undefined8 *)(puVar5 + lVar8 + 0x50) = uVar3;
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x50) + 8) = uVar4;
          uVar2 = *(undefined8 *)((long)(param_1 + lVar8 + 0x60) + 8);
          uVar3 = *(undefined8 *)(param_1 + lVar8 + 0x70);
          uVar4 = *(undefined8 *)((long)(param_1 + lVar8 + 0x70) + 8);
          *(undefined8 *)(puVar5 + lVar8 + 0x60) = *(undefined8 *)(param_1 + lVar8 + 0x60);
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x60) + 8) = uVar2;
          *(undefined8 *)(puVar5 + lVar8 + 0x70) = uVar3;
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x70) + 8) = uVar4;
          lVar8 = lVar8 + 0x80;
          lVar9 = lVar9 + 4;
          puVar13 = PTR_0010ce50;
        } while (lVar9 != 0);
      }
      PTR_0010ce50 = puVar13;
      if (uVar7 != 0) {
        lVar8 = lVar8 + 0x10;
        lVar9 = -uVar7;
        do {
          uVar2 = *(undefined8 *)((long)(param_1 + lVar8 + -0x10) + 8);
          uVar3 = *(undefined8 *)(param_1 + lVar8);
          uVar4 = *(undefined8 *)((long)(param_1 + lVar8) + 8);
          *(undefined8 *)(puVar13 + lVar8 + -0x10) = *(undefined8 *)(param_1 + lVar8 + -0x10);
          *(undefined8 *)((long)(puVar13 + lVar8 + -0x10) + 8) = uVar2;
          *(undefined8 *)(puVar13 + lVar8) = uVar3;
          *(undefined8 *)((long)(puVar13 + lVar8) + 8) = uVar4;
          lVar8 = lVar8 + 0x20;
          lVar9 = lVar9 + 1;
        } while (lVar9 != 0);
      }
      if (uVar1 == uVar11) goto LAB_00106f94;
      param_1 = param_1 + uVar11;
      puVar13 = PTR_0010ce50 + uVar11;
    }
    lVar9 = 0;
    do {
      puVar13[lVar9] = param_1[lVar9];
      lVar9 = lVar9 + 1;
    } while ((byte)((char)uVar10 + (char)lVar9) < bVar12);
  }
LAB_00106f94:
  *PTR_0010ce58 = bVar12;
  return uVar6;
}



// === x2com_req at 00107280 (406 bytes) ===

undefined8 x2com_req(undefined *param_1,byte param_2)

{
  ulong uVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined *puVar5;
  undefined8 uVar6;
  ulong uVar7;
  long lVar8;
  long lVar9;
  uint uVar10;
  byte bVar12;
  undefined *puVar13;
  ulong uVar11;
  
  puVar13 = PTR_0010ce60;
  if (*PTR_0010ce68 != '\0' || *PTR_0010ce60 != '\0') {
    return 0;
  }
  *PTR_0010ce60 = 1;
  puVar5 = PTR_0010ce70;
  uVar6 = CONCAT71((int7)((ulong)puVar13 >> 8),1);
  if (param_2 == 0) {
    return uVar6;
  }
  bVar12 = 0xe;
  if (param_2 < 0xe) {
    bVar12 = param_2;
  }
  if (bVar12 != 0) {
    uVar7 = (ulong)(byte)(bVar12 - 1);
    uVar1 = uVar7 + 1;
    if ((uVar1 < 0x20) ||
       ((PTR_0010ce70 < param_1 + uVar7 + 1 && (param_1 < PTR_0010ce70 + uVar7 + 1)))) {
      uVar10 = 0;
      puVar13 = PTR_0010ce70;
    }
    else {
      uVar10 = (uint)uVar1 & 0xffffffe0;
      uVar11 = (ulong)uVar10;
      lVar9 = (uVar11 - 0x20 >> 5) + 1;
      uVar7 = (ulong)((uint)lVar9 & 3);
      if (uVar11 - 0x20 < 0x60) {
        lVar8 = 0;
        puVar13 = PTR_0010ce70;
      }
      else {
        lVar9 = uVar7 - lVar9;
        lVar8 = 0;
        do {
          uVar2 = *(undefined8 *)((long)(param_1 + lVar8) + 8);
          uVar3 = *(undefined8 *)(param_1 + lVar8 + 0x10);
          uVar4 = *(undefined8 *)((long)(param_1 + lVar8 + 0x10) + 8);
          *(undefined8 *)(puVar5 + lVar8) = *(undefined8 *)(param_1 + lVar8);
          *(undefined8 *)((long)(puVar5 + lVar8) + 8) = uVar2;
          *(undefined8 *)(puVar5 + lVar8 + 0x10) = uVar3;
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x10) + 8) = uVar4;
          uVar2 = *(undefined8 *)((long)(param_1 + lVar8 + 0x20) + 8);
          uVar3 = *(undefined8 *)(param_1 + lVar8 + 0x30);
          uVar4 = *(undefined8 *)((long)(param_1 + lVar8 + 0x30) + 8);
          *(undefined8 *)(puVar5 + lVar8 + 0x20) = *(undefined8 *)(param_1 + lVar8 + 0x20);
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x20) + 8) = uVar2;
          *(undefined8 *)(puVar5 + lVar8 + 0x30) = uVar3;
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x30) + 8) = uVar4;
          uVar2 = *(undefined8 *)((long)(param_1 + lVar8 + 0x40) + 8);
          uVar3 = *(undefined8 *)(param_1 + lVar8 + 0x50);
          uVar4 = *(undefined8 *)((long)(param_1 + lVar8 + 0x50) + 8);
          *(undefined8 *)(puVar5 + lVar8 + 0x40) = *(undefined8 *)(param_1 + lVar8 + 0x40);
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x40) + 8) = uVar2;
          *(undefined8 *)(puVar5 + lVar8 + 0x50) = uVar3;
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x50) + 8) = uVar4;
          uVar2 = *(undefined8 *)((long)(param_1 + lVar8 + 0x60) + 8);
          uVar3 = *(undefined8 *)(param_1 + lVar8 + 0x70);
          uVar4 = *(undefined8 *)((long)(param_1 + lVar8 + 0x70) + 8);
          *(undefined8 *)(puVar5 + lVar8 + 0x60) = *(undefined8 *)(param_1 + lVar8 + 0x60);
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x60) + 8) = uVar2;
          *(undefined8 *)(puVar5 + lVar8 + 0x70) = uVar3;
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x70) + 8) = uVar4;
          lVar8 = lVar8 + 0x80;
          lVar9 = lVar9 + 4;
          puVar13 = PTR_0010ce70;
        } while (lVar9 != 0);
      }
      PTR_0010ce70 = puVar13;
      if (uVar7 != 0) {
        lVar8 = lVar8 + 0x10;
        lVar9 = -uVar7;
        do {
          uVar2 = *(undefined8 *)((long)(param_1 + lVar8 + -0x10) + 8);
          uVar3 = *(undefined8 *)(param_1 + lVar8);
          uVar4 = *(undefined8 *)((long)(param_1 + lVar8) + 8);
          *(undefined8 *)(puVar13 + lVar8 + -0x10) = *(undefined8 *)(param_1 + lVar8 + -0x10);
          *(undefined8 *)((long)(puVar13 + lVar8 + -0x10) + 8) = uVar2;
          *(undefined8 *)(puVar13 + lVar8) = uVar3;
          *(undefined8 *)((long)(puVar13 + lVar8) + 8) = uVar4;
          lVar8 = lVar8 + 0x20;
          lVar9 = lVar9 + 1;
        } while (lVar9 != 0);
      }
      if (uVar1 == uVar11) goto LAB_00107314;
      param_1 = param_1 + uVar11;
      puVar13 = PTR_0010ce70 + uVar11;
    }
    lVar9 = 0;
    do {
      puVar13[lVar9] = param_1[lVar9];
      lVar9 = lVar9 + 1;
    } while ((byte)((char)uVar10 + (char)lVar9) < bVar12);
  }
LAB_00107314:
  *PTR_0010ce78 = bVar12;
  return uVar6;
}



// === x2com_notify at 00109180 (406 bytes) ===

undefined8 x2com_notify(undefined *param_1,byte param_2)

{
  ulong uVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined *puVar5;
  undefined8 uVar6;
  ulong uVar7;
  long lVar8;
  long lVar9;
  uint uVar10;
  byte bVar12;
  undefined *puVar13;
  ulong uVar11;
  
  puVar13 = PTR_0010ced8;
  if (*PTR_0010cee0 != '\0' || *PTR_0010ced8 != '\0') {
    return 0;
  }
  *PTR_0010ced8 = 1;
  puVar5 = PTR_0010cf30;
  uVar6 = CONCAT71((int7)((ulong)puVar13 >> 8),1);
  if (param_2 == 0) {
    return uVar6;
  }
  bVar12 = 0xe;
  if (param_2 < 0xe) {
    bVar12 = param_2;
  }
  if (bVar12 != 0) {
    uVar7 = (ulong)(byte)(bVar12 - 1);
    uVar1 = uVar7 + 1;
    if ((uVar1 < 0x20) ||
       ((PTR_0010cf30 < param_1 + uVar7 + 1 && (param_1 < PTR_0010cf30 + uVar7 + 1)))) {
      uVar10 = 0;
      puVar13 = PTR_0010cf30;
    }
    else {
      uVar10 = (uint)uVar1 & 0xffffffe0;
      uVar11 = (ulong)uVar10;
      lVar9 = (uVar11 - 0x20 >> 5) + 1;
      uVar7 = (ulong)((uint)lVar9 & 3);
      if (uVar11 - 0x20 < 0x60) {
        lVar8 = 0;
        puVar13 = PTR_0010cf30;
      }
      else {
        lVar9 = uVar7 - lVar9;
        lVar8 = 0;
        do {
          uVar2 = *(undefined8 *)((long)(param_1 + lVar8) + 8);
          uVar3 = *(undefined8 *)(param_1 + lVar8 + 0x10);
          uVar4 = *(undefined8 *)((long)(param_1 + lVar8 + 0x10) + 8);
          *(undefined8 *)(puVar5 + lVar8) = *(undefined8 *)(param_1 + lVar8);
          *(undefined8 *)((long)(puVar5 + lVar8) + 8) = uVar2;
          *(undefined8 *)(puVar5 + lVar8 + 0x10) = uVar3;
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x10) + 8) = uVar4;
          uVar2 = *(undefined8 *)((long)(param_1 + lVar8 + 0x20) + 8);
          uVar3 = *(undefined8 *)(param_1 + lVar8 + 0x30);
          uVar4 = *(undefined8 *)((long)(param_1 + lVar8 + 0x30) + 8);
          *(undefined8 *)(puVar5 + lVar8 + 0x20) = *(undefined8 *)(param_1 + lVar8 + 0x20);
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x20) + 8) = uVar2;
          *(undefined8 *)(puVar5 + lVar8 + 0x30) = uVar3;
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x30) + 8) = uVar4;
          uVar2 = *(undefined8 *)((long)(param_1 + lVar8 + 0x40) + 8);
          uVar3 = *(undefined8 *)(param_1 + lVar8 + 0x50);
          uVar4 = *(undefined8 *)((long)(param_1 + lVar8 + 0x50) + 8);
          *(undefined8 *)(puVar5 + lVar8 + 0x40) = *(undefined8 *)(param_1 + lVar8 + 0x40);
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x40) + 8) = uVar2;
          *(undefined8 *)(puVar5 + lVar8 + 0x50) = uVar3;
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x50) + 8) = uVar4;
          uVar2 = *(undefined8 *)((long)(param_1 + lVar8 + 0x60) + 8);
          uVar3 = *(undefined8 *)(param_1 + lVar8 + 0x70);
          uVar4 = *(undefined8 *)((long)(param_1 + lVar8 + 0x70) + 8);
          *(undefined8 *)(puVar5 + lVar8 + 0x60) = *(undefined8 *)(param_1 + lVar8 + 0x60);
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x60) + 8) = uVar2;
          *(undefined8 *)(puVar5 + lVar8 + 0x70) = uVar3;
          *(undefined8 *)((long)(puVar5 + lVar8 + 0x70) + 8) = uVar4;
          lVar8 = lVar8 + 0x80;
          lVar9 = lVar9 + 4;
          puVar13 = PTR_0010cf30;
        } while (lVar9 != 0);
      }
      PTR_0010cf30 = puVar13;
      if (uVar7 != 0) {
        lVar8 = lVar8 + 0x10;
        lVar9 = -uVar7;
        do {
          uVar2 = *(undefined8 *)((long)(param_1 + lVar8 + -0x10) + 8);
          uVar3 = *(undefined8 *)(param_1 + lVar8);
          uVar4 = *(undefined8 *)((long)(param_1 + lVar8) + 8);
          *(undefined8 *)(puVar13 + lVar8 + -0x10) = *(undefined8 *)(param_1 + lVar8 + -0x10);
          *(undefined8 *)((long)(puVar13 + lVar8 + -0x10) + 8) = uVar2;
          *(undefined8 *)(puVar13 + lVar8) = uVar3;
          *(undefined8 *)((long)(puVar13 + lVar8) + 8) = uVar4;
          lVar8 = lVar8 + 0x20;
          lVar9 = lVar9 + 1;
        } while (lVar9 != 0);
      }
      if (uVar1 == uVar11) goto LAB_00109214;
      param_1 = param_1 + uVar11;
      puVar13 = PTR_0010cf30 + uVar11;
    }
    lVar9 = 0;
    do {
      puVar13[lVar9] = param_1[lVar9];
      lVar9 = lVar9 + 1;
    } while ((byte)((char)uVar10 + (char)lVar9) < bVar12);
  }
LAB_00109214:
  *DAT_0010cf38 = bVar12;
  return uVar6;
}



// === Java_com_quadzillapower_iQuad_bluetooth_BluetoothChatService_setAID at 00106810 (361 bytes) ===

undefined8
Java_com_quadzillapower_iQuad_bluetooth_BluetoothChatService_setAID
          (long *param_1,undefined8 param_2,int param_3,undefined8 param_4)

{
  long lVar1;
  long lVar2;
  ulong uVar3;
  long lVar4;
  long lVar5;
  ulong uVar6;
  undefined8 uVar7;
  long *plVar8;
  
  if (param_3 < 0x4b) {
    plVar8 = (long *)(PTR_one_byte_tx_p_0010cdf8 + (long)param_3 * 8);
    lVar4 = 4;
  }
  else if (param_3 < 0x96) {
    plVar8 = (long *)(PTR_two_byte_tx_p_0010ce00 + (long)param_3 * 8 + -600);
    lVar4 = 4;
  }
  else if (param_3 < 0xb9) {
    plVar8 = (long *)(PTR_three_byte_tx_p_0010ce08 + (long)param_3 * 8 + -0x4b0);
    lVar4 = 4;
  }
  else if (param_3 < 0xdc) {
    plVar8 = (long *)(PTR_four_byte_tx_p_0010ce10 + (long)param_3 * 8 + -0x5c8);
    lVar4 = 4;
  }
  else {
    plVar8 = (long *)(PTR_var_byte_tx_p_0010ce18 + (long)param_3 * 8 + -0x6e0);
    lVar4 = 0xd;
  }
  uVar7 = 0;
  lVar2 = (**(code **)(*param_1 + 0x5c0))(param_1,param_4,0);
  if (lVar2 != 0) {
    lVar1 = *plVar8;
    uVar3 = (ulong)((uint)lVar4 & 1);
    if (lVar4 - 1U < 3) {
      lVar5 = 0;
    }
    else {
      lVar5 = 0;
      do {
        *(undefined1 *)(lVar1 + lVar5) = *(undefined1 *)(lVar2 + lVar5);
        *(undefined1 *)(lVar1 + 1 + lVar5) = *(undefined1 *)(lVar2 + 1 + lVar5);
        *(undefined1 *)(lVar1 + 2 + lVar5) = *(undefined1 *)(lVar2 + 2 + lVar5);
        *(undefined1 *)(lVar1 + 3 + lVar5) = *(undefined1 *)(lVar2 + 3 + lVar5);
        lVar5 = lVar5 + 4;
      } while (lVar4 - uVar3 != lVar5);
    }
    if (uVar3 != 0) {
      uVar6 = 0;
      do {
        *(undefined1 *)(lVar1 + lVar5 + uVar6) = *(undefined1 *)(lVar2 + lVar5 + uVar6);
        uVar6 = uVar6 + 1;
      } while (uVar3 != uVar6);
    }
    (**(code **)(*param_1 + 0x600))(param_1,param_4,lVar2,0);
    uVar7 = 1;
  }
  return uVar7;
}



// === x2com_get_msg_data at 001060d0 (360 bytes) ===

int x2com_get_msg_data(byte *param_1,byte param_2,int param_3,byte *param_4,char *param_5)

{
  byte bVar1;
  undefined *puVar2;
  undefined *puVar3;
  ulong uVar4;
  byte bVar5;
  undefined8 *puVar6;
  char cVar7;
  byte bVar8;
  byte unaff_R12B;
  char cVar9;
  byte *unaff_R15;
  
  puVar3 = PTR_two_byte_rx_p_0010cdd8;
  puVar2 = PTR_one_byte_rx_p_0010cdd0;
  bVar8 = 0xe;
  if (param_2 < 0xe) {
    bVar8 = param_2;
  }
  if (bVar8 == 0) {
    cVar7 = '\0';
LAB_0010621e:
    *param_5 = cVar7;
    return 2 - (uint)(unaff_R12B == 0);
  }
  cVar9 = '\x01';
  cVar7 = '\0';
  bVar5 = 0;
  if (param_3 != 4) goto LAB_00106141;
  do {
    bVar1 = *param_1;
    param_1 = param_1 + 1;
    *param_4 = bVar1;
    param_4 = param_4 + 1;
    cVar7 = cVar7 + '\x01';
    while( true ) {
      bVar5 = bVar5 + 1;
      if (bVar8 <= bVar5) goto LAB_0010621e;
      if (param_3 == 4) break;
LAB_00106141:
      if (param_3 == 2) break;
      if (cVar9 == '\x02') {
        bVar1 = *param_1;
        param_1 = param_1 + 1;
        *unaff_R15 = bVar1;
        unaff_R15 = unaff_R15 + 1;
        unaff_R12B = unaff_R12B - 1;
        cVar9 = '\x02' - (unaff_R12B == 0);
      }
      else if (cVar9 == '\x01') {
        bVar1 = *param_1;
        uVar4 = (ulong)bVar1;
        if (uVar4 < 0x4b) {
          puVar6 = (undefined8 *)(puVar2 + uVar4 * 8);
          unaff_R12B = 1;
        }
        else if (bVar1 < 0x96) {
          puVar6 = (undefined8 *)(puVar3 + uVar4 * 8 + -600);
          unaff_R12B = 2;
        }
        else if (bVar1 < 0xb9) {
          puVar6 = (undefined8 *)(PTR_three_byte_rx_p_0010cde0 + uVar4 * 8 + -0x4b0);
          unaff_R12B = 3;
        }
        else if (bVar1 < 0xdc) {
          puVar6 = (undefined8 *)(PTR_four_byte_rx_p_0010cde8 + uVar4 * 8 + -0x5c8);
          unaff_R12B = 4;
        }
        else {
          unaff_R12B = param_1[1];
          puVar6 = (undefined8 *)(PTR_var_byte_rx_p_0010cdf0 + uVar4 * 8 + -0x6e0);
        }
        param_1 = param_1 + 1;
        unaff_R15 = (byte *)*puVar6;
        if (unaff_R15 == (byte *)0x0) {
          unaff_R15 = (byte *)0x0;
          cVar9 = '\0';
        }
        else {
          *param_4 = bVar1;
          param_4 = param_4 + 1;
          cVar7 = cVar7 + '\x01';
          cVar9 = '\x02';
        }
      }
      else {
        param_1 = param_1 + 1;
        unaff_R12B = unaff_R12B - 1;
        if (unaff_R12B == 0) {
          cVar9 = '\x01';
        }
      }
    }
  } while( true );
}



// === x2com_get_notify_aid_list at 00108a70 (358 bytes) ===

void x2com_get_notify_aid_list(undefined *param_1)

{
  ulong uVar1;
  byte bVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  undefined *puVar6;
  ulong uVar7;
  long lVar8;
  long lVar9;
  undefined *puVar10;
  uint uVar11;
  byte bVar13;
  ulong uVar12;
  
  puVar10 = PTR_0010cf30;
  if ((param_1 != (undefined *)0x0) && (bVar2 = *DAT_0010cf38, bVar2 != 0)) {
    bVar13 = 0xe;
    if (bVar2 < 0xe) {
      bVar13 = bVar2;
    }
    if (bVar13 != 0) {
      uVar7 = (ulong)(byte)(bVar13 - 1);
      uVar1 = uVar7 + 1;
      if ((uVar1 < 0x20) ||
         ((param_1 < PTR_0010cf30 + uVar7 + 1 && (PTR_0010cf30 < param_1 + uVar7 + 1)))) {
        uVar11 = 0;
      }
      else {
        uVar11 = (uint)uVar1 & 0xffffffe0;
        uVar12 = (ulong)uVar11;
        lVar8 = (uVar12 - 0x20 >> 5) + 1;
        uVar7 = (ulong)((uint)lVar8 & 3);
        if (uVar12 - 0x20 < 0x60) {
          lVar9 = 0;
          puVar6 = PTR_0010cf30;
        }
        else {
          lVar8 = uVar7 - lVar8;
          lVar9 = 0;
          do {
            uVar3 = *(undefined8 *)((long)(puVar10 + lVar9) + 8);
            uVar4 = *(undefined8 *)(puVar10 + lVar9 + 0x10);
            uVar5 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x10) + 8);
            *(undefined8 *)(param_1 + lVar9) = *(undefined8 *)(puVar10 + lVar9);
            *(undefined8 *)((long)(param_1 + lVar9) + 8) = uVar3;
            *(undefined8 *)(param_1 + lVar9 + 0x10) = uVar4;
            *(undefined8 *)((long)(param_1 + lVar9 + 0x10) + 8) = uVar5;
            uVar3 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x20) + 8);
            uVar4 = *(undefined8 *)(puVar10 + lVar9 + 0x30);
            uVar5 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x30) + 8);
            *(undefined8 *)(param_1 + lVar9 + 0x20) = *(undefined8 *)(puVar10 + lVar9 + 0x20);
            *(undefined8 *)((long)(param_1 + lVar9 + 0x20) + 8) = uVar3;
            *(undefined8 *)(param_1 + lVar9 + 0x30) = uVar4;
            *(undefined8 *)((long)(param_1 + lVar9 + 0x30) + 8) = uVar5;
            uVar3 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x40) + 8);
            uVar4 = *(undefined8 *)(puVar10 + lVar9 + 0x50);
            uVar5 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x50) + 8);
            *(undefined8 *)(param_1 + lVar9 + 0x40) = *(undefined8 *)(puVar10 + lVar9 + 0x40);
            *(undefined8 *)((long)(param_1 + lVar9 + 0x40) + 8) = uVar3;
            *(undefined8 *)(param_1 + lVar9 + 0x50) = uVar4;
            *(undefined8 *)((long)(param_1 + lVar9 + 0x50) + 8) = uVar5;
            uVar3 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x60) + 8);
            uVar4 = *(undefined8 *)(puVar10 + lVar9 + 0x70);
            uVar5 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x70) + 8);
            *(undefined8 *)(param_1 + lVar9 + 0x60) = *(undefined8 *)(puVar10 + lVar9 + 0x60);
            *(undefined8 *)((long)(param_1 + lVar9 + 0x60) + 8) = uVar3;
            *(undefined8 *)(param_1 + lVar9 + 0x70) = uVar4;
            *(undefined8 *)((long)(param_1 + lVar9 + 0x70) + 8) = uVar5;
            lVar9 = lVar9 + 0x80;
            lVar8 = lVar8 + 4;
            puVar6 = PTR_0010cf30;
          } while (lVar8 != 0);
        }
        PTR_0010cf30 = puVar6;
        if (uVar7 != 0) {
          lVar9 = lVar9 + 0x10;
          lVar8 = -uVar7;
          do {
            uVar3 = *(undefined8 *)((long)(puVar6 + lVar9 + -0x10) + 8);
            uVar4 = *(undefined8 *)(puVar6 + lVar9);
            uVar5 = *(undefined8 *)((long)(puVar6 + lVar9) + 8);
            *(undefined8 *)(param_1 + lVar9 + -0x10) = *(undefined8 *)(puVar6 + lVar9 + -0x10);
            *(undefined8 *)((long)(param_1 + lVar9 + -0x10) + 8) = uVar3;
            *(undefined8 *)(param_1 + lVar9) = uVar4;
            *(undefined8 *)((long)(param_1 + lVar9) + 8) = uVar5;
            lVar9 = lVar9 + 0x20;
            lVar8 = lVar8 + 1;
          } while (lVar8 != 0);
        }
        if (uVar1 == uVar12) {
          return;
        }
        param_1 = param_1 + uVar12;
        puVar10 = PTR_0010cf30 + uVar12;
      }
      lVar8 = 0;
      do {
        param_1[lVar8] = puVar10[lVar8];
        lVar8 = lVar8 + 1;
      } while ((byte)((char)uVar11 + (char)lVar8) < bVar13);
    }
  }
  return;
}



// === x2com_get_cmd_aid_list at 00108d30 (358 bytes) ===

void x2com_get_cmd_aid_list(undefined *param_1)

{
  ulong uVar1;
  byte bVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  undefined *puVar6;
  ulong uVar7;
  long lVar8;
  long lVar9;
  undefined *puVar10;
  uint uVar11;
  byte bVar13;
  ulong uVar12;
  
  puVar10 = PTR_0010ce30;
  if ((param_1 != (undefined *)0x0) && (bVar2 = *PTR_0010ce38, bVar2 != 0)) {
    bVar13 = 0xe;
    if (bVar2 < 0xe) {
      bVar13 = bVar2;
    }
    if (bVar13 != 0) {
      uVar7 = (ulong)(byte)(bVar13 - 1);
      uVar1 = uVar7 + 1;
      if ((uVar1 < 0x20) ||
         ((param_1 < PTR_0010ce30 + uVar7 + 1 && (PTR_0010ce30 < param_1 + uVar7 + 1)))) {
        uVar11 = 0;
      }
      else {
        uVar11 = (uint)uVar1 & 0xffffffe0;
        uVar12 = (ulong)uVar11;
        lVar8 = (uVar12 - 0x20 >> 5) + 1;
        uVar7 = (ulong)((uint)lVar8 & 3);
        if (uVar12 - 0x20 < 0x60) {
          lVar9 = 0;
          puVar6 = PTR_0010ce30;
        }
        else {
          lVar8 = uVar7 - lVar8;
          lVar9 = 0;
          do {
            uVar3 = *(undefined8 *)((long)(puVar10 + lVar9) + 8);
            uVar4 = *(undefined8 *)(puVar10 + lVar9 + 0x10);
            uVar5 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x10) + 8);
            *(undefined8 *)(param_1 + lVar9) = *(undefined8 *)(puVar10 + lVar9);
            *(undefined8 *)((long)(param_1 + lVar9) + 8) = uVar3;
            *(undefined8 *)(param_1 + lVar9 + 0x10) = uVar4;
            *(undefined8 *)((long)(param_1 + lVar9 + 0x10) + 8) = uVar5;
            uVar3 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x20) + 8);
            uVar4 = *(undefined8 *)(puVar10 + lVar9 + 0x30);
            uVar5 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x30) + 8);
            *(undefined8 *)(param_1 + lVar9 + 0x20) = *(undefined8 *)(puVar10 + lVar9 + 0x20);
            *(undefined8 *)((long)(param_1 + lVar9 + 0x20) + 8) = uVar3;
            *(undefined8 *)(param_1 + lVar9 + 0x30) = uVar4;
            *(undefined8 *)((long)(param_1 + lVar9 + 0x30) + 8) = uVar5;
            uVar3 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x40) + 8);
            uVar4 = *(undefined8 *)(puVar10 + lVar9 + 0x50);
            uVar5 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x50) + 8);
            *(undefined8 *)(param_1 + lVar9 + 0x40) = *(undefined8 *)(puVar10 + lVar9 + 0x40);
            *(undefined8 *)((long)(param_1 + lVar9 + 0x40) + 8) = uVar3;
            *(undefined8 *)(param_1 + lVar9 + 0x50) = uVar4;
            *(undefined8 *)((long)(param_1 + lVar9 + 0x50) + 8) = uVar5;
            uVar3 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x60) + 8);
            uVar4 = *(undefined8 *)(puVar10 + lVar9 + 0x70);
            uVar5 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x70) + 8);
            *(undefined8 *)(param_1 + lVar9 + 0x60) = *(undefined8 *)(puVar10 + lVar9 + 0x60);
            *(undefined8 *)((long)(param_1 + lVar9 + 0x60) + 8) = uVar3;
            *(undefined8 *)(param_1 + lVar9 + 0x70) = uVar4;
            *(undefined8 *)((long)(param_1 + lVar9 + 0x70) + 8) = uVar5;
            lVar9 = lVar9 + 0x80;
            lVar8 = lVar8 + 4;
            puVar6 = PTR_0010ce30;
          } while (lVar8 != 0);
        }
        PTR_0010ce30 = puVar6;
        if (uVar7 != 0) {
          lVar9 = lVar9 + 0x10;
          lVar8 = -uVar7;
          do {
            uVar3 = *(undefined8 *)((long)(puVar6 + lVar9 + -0x10) + 8);
            uVar4 = *(undefined8 *)(puVar6 + lVar9);
            uVar5 = *(undefined8 *)((long)(puVar6 + lVar9) + 8);
            *(undefined8 *)(param_1 + lVar9 + -0x10) = *(undefined8 *)(puVar6 + lVar9 + -0x10);
            *(undefined8 *)((long)(param_1 + lVar9 + -0x10) + 8) = uVar3;
            *(undefined8 *)(param_1 + lVar9) = uVar4;
            *(undefined8 *)((long)(param_1 + lVar9) + 8) = uVar5;
            lVar9 = lVar9 + 0x20;
            lVar8 = lVar8 + 1;
          } while (lVar8 != 0);
        }
        if (uVar1 == uVar12) {
          return;
        }
        param_1 = param_1 + uVar12;
        puVar10 = PTR_0010ce30 + uVar12;
      }
      lVar8 = 0;
      do {
        param_1[lVar8] = puVar10[lVar8];
        lVar8 = lVar8 + 1;
      } while ((byte)((char)uVar11 + (char)lVar8) < bVar13);
    }
  }
  return;
}



// === x2com_get_cwa_aid_list at 00108ea0 (358 bytes) ===

void x2com_get_cwa_aid_list(undefined *param_1)

{
  ulong uVar1;
  byte bVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  undefined *puVar6;
  ulong uVar7;
  long lVar8;
  long lVar9;
  undefined *puVar10;
  uint uVar11;
  byte bVar13;
  ulong uVar12;
  
  puVar10 = PTR_0010ce50;
  if ((param_1 != (undefined *)0x0) && (bVar2 = *PTR_0010ce58, bVar2 != 0)) {
    bVar13 = 0xe;
    if (bVar2 < 0xe) {
      bVar13 = bVar2;
    }
    if (bVar13 != 0) {
      uVar7 = (ulong)(byte)(bVar13 - 1);
      uVar1 = uVar7 + 1;
      if ((uVar1 < 0x20) ||
         ((param_1 < PTR_0010ce50 + uVar7 + 1 && (PTR_0010ce50 < param_1 + uVar7 + 1)))) {
        uVar11 = 0;
      }
      else {
        uVar11 = (uint)uVar1 & 0xffffffe0;
        uVar12 = (ulong)uVar11;
        lVar8 = (uVar12 - 0x20 >> 5) + 1;
        uVar7 = (ulong)((uint)lVar8 & 3);
        if (uVar12 - 0x20 < 0x60) {
          lVar9 = 0;
          puVar6 = PTR_0010ce50;
        }
        else {
          lVar8 = uVar7 - lVar8;
          lVar9 = 0;
          do {
            uVar3 = *(undefined8 *)((long)(puVar10 + lVar9) + 8);
            uVar4 = *(undefined8 *)(puVar10 + lVar9 + 0x10);
            uVar5 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x10) + 8);
            *(undefined8 *)(param_1 + lVar9) = *(undefined8 *)(puVar10 + lVar9);
            *(undefined8 *)((long)(param_1 + lVar9) + 8) = uVar3;
            *(undefined8 *)(param_1 + lVar9 + 0x10) = uVar4;
            *(undefined8 *)((long)(param_1 + lVar9 + 0x10) + 8) = uVar5;
            uVar3 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x20) + 8);
            uVar4 = *(undefined8 *)(puVar10 + lVar9 + 0x30);
            uVar5 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x30) + 8);
            *(undefined8 *)(param_1 + lVar9 + 0x20) = *(undefined8 *)(puVar10 + lVar9 + 0x20);
            *(undefined8 *)((long)(param_1 + lVar9 + 0x20) + 8) = uVar3;
            *(undefined8 *)(param_1 + lVar9 + 0x30) = uVar4;
            *(undefined8 *)((long)(param_1 + lVar9 + 0x30) + 8) = uVar5;
            uVar3 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x40) + 8);
            uVar4 = *(undefined8 *)(puVar10 + lVar9 + 0x50);
            uVar5 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x50) + 8);
            *(undefined8 *)(param_1 + lVar9 + 0x40) = *(undefined8 *)(puVar10 + lVar9 + 0x40);
            *(undefined8 *)((long)(param_1 + lVar9 + 0x40) + 8) = uVar3;
            *(undefined8 *)(param_1 + lVar9 + 0x50) = uVar4;
            *(undefined8 *)((long)(param_1 + lVar9 + 0x50) + 8) = uVar5;
            uVar3 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x60) + 8);
            uVar4 = *(undefined8 *)(puVar10 + lVar9 + 0x70);
            uVar5 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x70) + 8);
            *(undefined8 *)(param_1 + lVar9 + 0x60) = *(undefined8 *)(puVar10 + lVar9 + 0x60);
            *(undefined8 *)((long)(param_1 + lVar9 + 0x60) + 8) = uVar3;
            *(undefined8 *)(param_1 + lVar9 + 0x70) = uVar4;
            *(undefined8 *)((long)(param_1 + lVar9 + 0x70) + 8) = uVar5;
            lVar9 = lVar9 + 0x80;
            lVar8 = lVar8 + 4;
            puVar6 = PTR_0010ce50;
          } while (lVar8 != 0);
        }
        PTR_0010ce50 = puVar6;
        if (uVar7 != 0) {
          lVar9 = lVar9 + 0x10;
          lVar8 = -uVar7;
          do {
            uVar3 = *(undefined8 *)((long)(puVar6 + lVar9 + -0x10) + 8);
            uVar4 = *(undefined8 *)(puVar6 + lVar9);
            uVar5 = *(undefined8 *)((long)(puVar6 + lVar9) + 8);
            *(undefined8 *)(param_1 + lVar9 + -0x10) = *(undefined8 *)(puVar6 + lVar9 + -0x10);
            *(undefined8 *)((long)(param_1 + lVar9 + -0x10) + 8) = uVar3;
            *(undefined8 *)(param_1 + lVar9) = uVar4;
            *(undefined8 *)((long)(param_1 + lVar9) + 8) = uVar5;
            lVar9 = lVar9 + 0x20;
            lVar8 = lVar8 + 1;
          } while (lVar8 != 0);
        }
        if (uVar1 == uVar12) {
          return;
        }
        param_1 = param_1 + uVar12;
        puVar10 = PTR_0010ce50 + uVar12;
      }
      lVar8 = 0;
      do {
        param_1[lVar8] = puVar10[lVar8];
        lVar8 = lVar8 + 1;
      } while ((byte)((char)uVar11 + (char)lVar8) < bVar13);
    }
  }
  return;
}



// === x2com_get_req_aid_list at 00109010 (358 bytes) ===

void x2com_get_req_aid_list(undefined *param_1)

{
  ulong uVar1;
  byte bVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  undefined *puVar6;
  ulong uVar7;
  long lVar8;
  long lVar9;
  undefined *puVar10;
  uint uVar11;
  byte bVar13;
  ulong uVar12;
  
  puVar10 = PTR_0010ce70;
  if ((param_1 != (undefined *)0x0) && (bVar2 = *PTR_0010ce78, bVar2 != 0)) {
    bVar13 = 0xe;
    if (bVar2 < 0xe) {
      bVar13 = bVar2;
    }
    if (bVar13 != 0) {
      uVar7 = (ulong)(byte)(bVar13 - 1);
      uVar1 = uVar7 + 1;
      if ((uVar1 < 0x20) ||
         ((param_1 < PTR_0010ce70 + uVar7 + 1 && (PTR_0010ce70 < param_1 + uVar7 + 1)))) {
        uVar11 = 0;
      }
      else {
        uVar11 = (uint)uVar1 & 0xffffffe0;
        uVar12 = (ulong)uVar11;
        lVar8 = (uVar12 - 0x20 >> 5) + 1;
        uVar7 = (ulong)((uint)lVar8 & 3);
        if (uVar12 - 0x20 < 0x60) {
          lVar9 = 0;
          puVar6 = PTR_0010ce70;
        }
        else {
          lVar8 = uVar7 - lVar8;
          lVar9 = 0;
          do {
            uVar3 = *(undefined8 *)((long)(puVar10 + lVar9) + 8);
            uVar4 = *(undefined8 *)(puVar10 + lVar9 + 0x10);
            uVar5 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x10) + 8);
            *(undefined8 *)(param_1 + lVar9) = *(undefined8 *)(puVar10 + lVar9);
            *(undefined8 *)((long)(param_1 + lVar9) + 8) = uVar3;
            *(undefined8 *)(param_1 + lVar9 + 0x10) = uVar4;
            *(undefined8 *)((long)(param_1 + lVar9 + 0x10) + 8) = uVar5;
            uVar3 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x20) + 8);
            uVar4 = *(undefined8 *)(puVar10 + lVar9 + 0x30);
            uVar5 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x30) + 8);
            *(undefined8 *)(param_1 + lVar9 + 0x20) = *(undefined8 *)(puVar10 + lVar9 + 0x20);
            *(undefined8 *)((long)(param_1 + lVar9 + 0x20) + 8) = uVar3;
            *(undefined8 *)(param_1 + lVar9 + 0x30) = uVar4;
            *(undefined8 *)((long)(param_1 + lVar9 + 0x30) + 8) = uVar5;
            uVar3 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x40) + 8);
            uVar4 = *(undefined8 *)(puVar10 + lVar9 + 0x50);
            uVar5 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x50) + 8);
            *(undefined8 *)(param_1 + lVar9 + 0x40) = *(undefined8 *)(puVar10 + lVar9 + 0x40);
            *(undefined8 *)((long)(param_1 + lVar9 + 0x40) + 8) = uVar3;
            *(undefined8 *)(param_1 + lVar9 + 0x50) = uVar4;
            *(undefined8 *)((long)(param_1 + lVar9 + 0x50) + 8) = uVar5;
            uVar3 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x60) + 8);
            uVar4 = *(undefined8 *)(puVar10 + lVar9 + 0x70);
            uVar5 = *(undefined8 *)((long)(puVar10 + lVar9 + 0x70) + 8);
            *(undefined8 *)(param_1 + lVar9 + 0x60) = *(undefined8 *)(puVar10 + lVar9 + 0x60);
            *(undefined8 *)((long)(param_1 + lVar9 + 0x60) + 8) = uVar3;
            *(undefined8 *)(param_1 + lVar9 + 0x70) = uVar4;
            *(undefined8 *)((long)(param_1 + lVar9 + 0x70) + 8) = uVar5;
            lVar9 = lVar9 + 0x80;
            lVar8 = lVar8 + 4;
            puVar6 = PTR_0010ce70;
          } while (lVar8 != 0);
        }
        PTR_0010ce70 = puVar6;
        if (uVar7 != 0) {
          lVar9 = lVar9 + 0x10;
          lVar8 = -uVar7;
          do {
            uVar3 = *(undefined8 *)((long)(puVar6 + lVar9 + -0x10) + 8);
            uVar4 = *(undefined8 *)(puVar6 + lVar9);
            uVar5 = *(undefined8 *)((long)(puVar6 + lVar9) + 8);
            *(undefined8 *)(param_1 + lVar9 + -0x10) = *(undefined8 *)(puVar6 + lVar9 + -0x10);
            *(undefined8 *)((long)(param_1 + lVar9 + -0x10) + 8) = uVar3;
            *(undefined8 *)(param_1 + lVar9) = uVar4;
            *(undefined8 *)((long)(param_1 + lVar9) + 8) = uVar5;
            lVar9 = lVar9 + 0x20;
            lVar8 = lVar8 + 1;
          } while (lVar8 != 0);
        }
        if (uVar1 == uVar12) {
          return;
        }
        param_1 = param_1 + uVar12;
        puVar10 = PTR_0010ce70 + uVar12;
      }
      lVar8 = 0;
      do {
        param_1[lVar8] = puVar10[lVar8];
        lVar8 = lVar8 + 1;
      } while ((byte)((char)uVar11 + (char)lVar8) < bVar13);
    }
  }
  return;
}



// === x2com_copy_list at 00108be0 (335 bytes) ===

void x2com_copy_list(ulong param_1,byte *param_2,ulong param_3,byte param_4)

{
  ulong uVar1;
  undefined8 *puVar2;
  undefined8 *puVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  undefined8 uVar6;
  ulong uVar7;
  long lVar8;
  long lVar9;
  uint uVar10;
  byte bVar11;
  ulong uVar12;
  
  if (param_1 == 0) {
    return;
  }
  if (param_4 == 0) {
    return;
  }
  bVar11 = 0xe;
  if (param_4 < 0xe) {
    bVar11 = param_4;
  }
  if (bVar11 != 0) {
    uVar7 = (ulong)(byte)(bVar11 - 1);
    uVar1 = uVar7 + 1;
    if ((uVar1 < 0x20) || ((param_1 < param_3 + uVar7 + 1 && (param_3 < uVar7 + param_1 + 1)))) {
      uVar10 = 0;
    }
    else {
      uVar10 = (uint)uVar1 & 0xffffffe0;
      uVar7 = (ulong)uVar10;
      lVar9 = (uVar7 - 0x20 >> 5) + 1;
      uVar12 = (ulong)((uint)lVar9 & 3);
      if (uVar7 - 0x20 < 0x60) {
        lVar8 = 0;
      }
      else {
        lVar9 = uVar12 - lVar9;
        lVar8 = 0;
        do {
          uVar4 = ((undefined8 *)(param_3 + lVar8))[1];
          puVar2 = (undefined8 *)(param_3 + 0x10 + lVar8);
          uVar5 = *puVar2;
          uVar6 = puVar2[1];
          *(undefined8 *)(param_1 + lVar8) = *(undefined8 *)(param_3 + lVar8);
          ((undefined8 *)(param_1 + lVar8))[1] = uVar4;
          puVar2 = (undefined8 *)(param_1 + 0x10 + lVar8);
          *puVar2 = uVar5;
          puVar2[1] = uVar6;
          puVar2 = (undefined8 *)(param_3 + 0x20 + lVar8);
          uVar4 = puVar2[1];
          puVar3 = (undefined8 *)(param_3 + 0x30 + lVar8);
          uVar5 = *puVar3;
          uVar6 = puVar3[1];
          puVar3 = (undefined8 *)(param_1 + 0x20 + lVar8);
          *puVar3 = *puVar2;
          puVar3[1] = uVar4;
          puVar2 = (undefined8 *)(param_1 + 0x30 + lVar8);
          *puVar2 = uVar5;
          puVar2[1] = uVar6;
          puVar2 = (undefined8 *)(param_3 + 0x40 + lVar8);
          uVar4 = puVar2[1];
          puVar3 = (undefined8 *)(param_3 + 0x50 + lVar8);
          uVar5 = *puVar3;
          uVar6 = puVar3[1];
          puVar3 = (undefined8 *)(param_1 + 0x40 + lVar8);
          *puVar3 = *puVar2;
          puVar3[1] = uVar4;
          puVar2 = (undefined8 *)(param_1 + 0x50 + lVar8);
          *puVar2 = uVar5;
          puVar2[1] = uVar6;
          puVar2 = (undefined8 *)(param_3 + 0x60 + lVar8);
          uVar4 = puVar2[1];
          puVar3 = (undefined8 *)(param_3 + 0x70 + lVar8);
          uVar5 = *puVar3;
          uVar6 = puVar3[1];
          puVar3 = (undefined8 *)(param_1 + 0x60 + lVar8);
          *puVar3 = *puVar2;
          puVar3[1] = uVar4;
          puVar2 = (undefined8 *)(param_1 + 0x70 + lVar8);
          *puVar2 = uVar5;
          puVar2[1] = uVar6;
          lVar8 = lVar8 + 0x80;
          lVar9 = lVar9 + 4;
        } while (lVar9 != 0);
      }
      if (uVar12 != 0) {
        lVar8 = lVar8 + 0x10;
        lVar9 = -uVar12;
        do {
          puVar2 = (undefined8 *)((param_3 - 0x10) + lVar8);
          uVar4 = puVar2[1];
          uVar5 = *(undefined8 *)(param_3 + lVar8);
          uVar6 = ((undefined8 *)(param_3 + lVar8))[1];
          puVar3 = (undefined8 *)((param_1 - 0x10) + lVar8);
          *puVar3 = *puVar2;
          puVar3[1] = uVar4;
          *(undefined8 *)(param_1 + lVar8) = uVar5;
          ((undefined8 *)(param_1 + lVar8))[1] = uVar6;
          lVar8 = lVar8 + 0x20;
          lVar9 = lVar9 + 1;
        } while (lVar9 != 0);
      }
      if (uVar1 == uVar7) goto LAB_00108c54;
      param_3 = param_3 + uVar7;
      param_1 = param_1 + uVar7;
    }
    lVar9 = 0;
    do {
      *(undefined1 *)(param_1 + lVar9) = *(undefined1 *)(param_3 + lVar9);
      lVar9 = lVar9 + 1;
    } while ((byte)((char)uVar10 + (char)lVar9) < bVar11);
  }
LAB_00108c54:
  *param_2 = bVar11;
  return;
}



// === Java_com_quadzillapower_iQuad_bluetooth_BluetoothChatService_getAID at 00106720 (235 bytes) ===

long Java_com_quadzillapower_iQuad_bluetooth_BluetoothChatService_getAID
               (long *param_1,undefined8 param_2,int param_3)

{
  long lVar1;
  undefined8 *puVar2;
  undefined8 uVar3;
  
  if (param_3 < 0x4b) {
    puVar2 = (undefined8 *)(PTR_one_byte_rx_p_0010cdd0 + (long)param_3 * 8);
    uVar3 = 4;
  }
  else if (param_3 < 0x96) {
    puVar2 = (undefined8 *)(PTR_two_byte_rx_p_0010cdd8 + (long)param_3 * 8 + -600);
    uVar3 = 4;
  }
  else if (param_3 < 0xb9) {
    puVar2 = (undefined8 *)(PTR_three_byte_rx_p_0010cde0 + (long)param_3 * 8 + -0x4b0);
    uVar3 = 4;
  }
  else if (param_3 < 0xdc) {
    puVar2 = (undefined8 *)(PTR_four_byte_rx_p_0010cde8 + (long)param_3 * 8 + -0x5c8);
    uVar3 = 4;
  }
  else {
    puVar2 = (undefined8 *)(PTR_var_byte_rx_p_0010cdf0 + (long)param_3 * 8 + -0x6e0);
    uVar3 = 0xd;
  }
  lVar1 = (**(code **)(*param_1 + 0x580))(param_1,uVar3);
  if (lVar1 != 0) {
    (**(code **)(*param_1 + 0x680))(param_1,lVar1,0,uVar3,*puVar2);
  }
  return lVar1;
}



// === x2com_tx_msg at 001057c0 (230 bytes) ===

void x2com_tx_msg(long *param_1,undefined8 param_2,undefined8 param_3,undefined1 param_4)

{
  long lVar1;
  long lVar2;
  long lVar3;
  
  lVar1 = (**(code **)(*param_1 + 0x30))
                    (param_1,"com/quadzillapower/iQuad/bluetooth/BluetoothChatService");
  if (lVar1 != 0) {
    lVar2 = (**(code **)(*param_1 + 0x108))(param_1,lVar1,"writeAV","([B)V");
    if (lVar2 != 0) {
      lVar3 = (**(code **)(*param_1 + 0x580))(param_1,param_4);
      if (lVar3 != 0) {
        (**(code **)(*param_1 + 0x680))(param_1,lVar3,0,param_4,param_3);
        (**(code **)(*param_1 + 0x1e8))(param_1,param_2,lVar2,lVar3);
        (**(code **)(*param_1 + 0xb8))(param_1,lVar3);
      }
                    /* WARNING: Could not recover jumptable at 0x00105895. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      (**(code **)(*param_1 + 0xb8))(param_1,lVar1);
      return;
    }
  }
  return;
}



// === x2com_update_aid_list at 00109320 (210 bytes) ===

void x2com_update_aid_list(void *param_1,byte *param_2,long param_3,byte param_4)

{
  byte bVar1;
  char cVar2;
  ulong uVar3;
  uint uVar4;
  ulong uVar5;
  byte bVar6;
  long in_FS_OFFSET;
  undefined1 local_36 [14];
  long local_28;
  
  local_28 = *(long *)(in_FS_OFFSET + 0x28);
  bVar6 = 0;
  if ((param_1 != (void *)0x0) && (bVar6 = 0, param_4 != 0)) {
    bVar1 = *param_2;
    if ((ulong)bVar1 != 0) {
      uVar4 = 0xe;
      if (param_4 < 0xe) {
        uVar4 = (uint)param_4;
      }
      uVar5 = 0;
      bVar6 = 0;
      do {
        uVar3 = 1;
        do {
          cVar2 = *(char *)(param_3 + -1 + uVar3);
          if (uVar4 <= uVar3) break;
          uVar3 = uVar3 + 1;
        } while (*(char *)((long)param_1 + uVar5) != cVar2);
        if (*(char *)((long)param_1 + uVar5) != cVar2) {
          uVar3 = (ulong)bVar6;
          bVar6 = bVar6 + 1;
          local_36[uVar3] = *(undefined1 *)((long)param_1 + uVar5);
        }
        uVar5 = uVar5 + 1;
      } while (uVar5 < bVar1);
      if (bVar6 != 0) {
        memcpy(param_1,local_36,(ulong)bVar6);
        goto LAB_001093cf;
      }
    }
    bVar6 = 0;
  }
LAB_001093cf:
  *param_2 = bVar6;
  if (*(long *)(in_FS_OFFSET + 0x28) == local_28) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



// === Java_com_quadzillapower_iQuad_bluetooth_BluetoothChatService_X2comRcv at 00107620 (200 bytes) ===

undefined4
Java_com_quadzillapower_iQuad_bluetooth_BluetoothChatService_X2comRcv
          (long *param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  undefined4 uVar1;
  long lVar2;
  undefined1 *puVar3;
  long in_FS_OFFSET;
  undefined1 local_39;
  long local_38;
  
  local_38 = *(long *)(in_FS_OFFSET + 0x28);
  uVar1 = 0;
  lVar2 = (**(code **)(*param_1 + 0x5c0))(param_1,param_3,0);
  puVar3 = (undefined1 *)(**(code **)(*param_1 + 0x5c0))(param_1,param_4,0);
  if ((lVar2 != 0) && (puVar3 != (undefined1 *)0x0)) {
    uVar1 = x2com_rcv(param_1,param_2,lVar2,&local_39);
    *puVar3 = local_39;
    (**(code **)(*param_1 + 0x600))(param_1,param_4,puVar3,0);
    (**(code **)(*param_1 + 0x600))(param_1,param_3,lVar2,0);
  }
  if (*(long *)(in_FS_OFFSET + 0x28) == local_38) {
    return uVar1;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



// === x2com_parse_msg at 00106630 (139 bytes) ===

undefined8 x2com_parse_msg(byte *param_1,uint *param_2,undefined8 param_3,undefined1 *param_4)

{
  byte bVar1;
  char cVar2;
  undefined8 uVar3;
  byte bVar4;
  uint uVar5;
  
  *param_2 = 6;
  *param_4 = 0;
  bVar1 = *param_1;
  bVar4 = bVar1 & 0xf;
  if (bVar4 == 0) {
    uVar3 = 5;
  }
  else {
    cVar2 = x2com_generate_crc(param_1,bVar4 + 1);
    uVar3 = 4;
    if (cVar2 == ';') {
      uVar5 = (uint)(bVar1 >> 4);
      *param_2 = uVar5;
      uVar3 = x2com_get_msg_data(param_1 + 1,bVar4 - 1,uVar5,param_3,param_4);
      return uVar3;
    }
  }
  return uVar3;
}



// === x2com_find_rx_storage at 00105fb0 (133 bytes) ===

undefined8 x2com_find_rx_storage(uint param_1)

{
  byte bVar1;
  
  bVar1 = (byte)param_1;
  if (bVar1 < 0x4b) {
    return *(undefined8 *)(PTR_one_byte_rx_p_0010cdd0 + (ulong)(param_1 & 0xff) * 8);
  }
  if (bVar1 < 0x96) {
    return *(undefined8 *)(PTR_two_byte_rx_p_0010cdd8 + (ulong)param_1 * 8 + -600);
  }
  if (bVar1 < 0xb9) {
    return *(undefined8 *)(PTR_three_byte_rx_p_0010cde0 + (ulong)param_1 * 8 + -0x4b0);
  }
  if (bVar1 < 0xdc) {
    return *(undefined8 *)(PTR_four_byte_rx_p_0010cde8 + (ulong)param_1 * 8 + -0x5c8);
  }
  return *(undefined8 *)(PTR_var_byte_rx_p_0010cdf0 + (ulong)param_1 * 8 + -0x6e0);
}



// === x2com_find_tx_storage at 00106040 (133 bytes) ===

undefined8 x2com_find_tx_storage(uint param_1)

{
  byte bVar1;
  
  bVar1 = (byte)param_1;
  if (bVar1 < 0x4b) {
    return *(undefined8 *)(PTR_one_byte_tx_p_0010cdf8 + (ulong)(param_1 & 0xff) * 8);
  }
  if (bVar1 < 0x96) {
    return *(undefined8 *)(PTR_two_byte_tx_p_0010ce00 + (ulong)param_1 * 8 + -600);
  }
  if (bVar1 < 0xb9) {
    return *(undefined8 *)(PTR_three_byte_tx_p_0010ce08 + (ulong)param_1 * 8 + -0x4b0);
  }
  if (bVar1 < 0xdc) {
    return *(undefined8 *)(PTR_four_byte_tx_p_0010ce10 + (ulong)param_1 * 8 + -0x5c8);
  }
  return *(undefined8 *)(PTR_var_byte_tx_p_0010ce18 + (ulong)param_1 * 8 + -0x6e0);
}



// === x2com_is_rx_msg_ready at 00105930 (125 bytes) ===

bool x2com_is_rx_msg_ready(long *param_1,undefined8 param_2)

{
  int iVar1;
  long lVar2;
  long lVar3;
  
  lVar2 = (**(code **)(*param_1 + 0x30))
                    (param_1,"com/quadzillapower/iQuad/bluetooth/BluetoothChatService");
  if ((lVar2 != 0) &&
     (lVar3 = (**(code **)(*param_1 + 0x108))(param_1,lVar2,"getCount",&DAT_00109449), lVar3 != 0))
  {
    iVar1 = (**(code **)(*param_1 + 0x188))(param_1,param_2,lVar3);
    (**(code **)(*param_1 + 0xb8))(param_1,lVar2);
    return 0 < iVar1;
  }
  return false;
}



// === x2com_is_tx_ready at 001058b0 (122 bytes) ===

undefined4 x2com_is_tx_ready(long *param_1,undefined8 param_2)

{
  undefined4 uVar1;
  long lVar2;
  long lVar3;
  
  lVar2 = (**(code **)(*param_1 + 0x30))
                    (param_1,"com/quadzillapower/iQuad/bluetooth/BluetoothChatService");
  if ((lVar2 != 0) &&
     (lVar3 = (**(code **)(*param_1 + 0x108))(param_1,lVar2,"getWriteStatus",&DAT_00109449),
     lVar3 != 0)) {
    uVar1 = (**(code **)(*param_1 + 0x188))(param_1,param_2,lVar3);
    (**(code **)(*param_1 + 0xb8))(param_1,lVar2);
    return uVar1;
  }
  return 0;
}



// === Java_com_quadzillapower_iQuad_bluetooth_BluetoothChatService_X2comInit at 00107520 (121 bytes) ===

void Java_com_quadzillapower_iQuad_bluetooth_BluetoothChatService_X2comInit(void)

{
  *PTR_0010cec0 = 0;
  *PTR_0010cec8 = 0;
  *PTR_0010ced0 = 0;
  *PTR_0010ce20 = 0;
  *PTR_0010ce28 = 0;
  *PTR_0010ced8 = 0;
  *PTR_0010cee0 = 0;
  *PTR_0010ce48 = 0;
  *PTR_0010cea8 = 0;
  *PTR_0010ce60 = 0;
  *PTR_0010ce68 = 0;
  *PTR_0010ce88 = 0;
  return;
}



// === x2com_init at 001075a0 (121 bytes) ===

void x2com_init(void)

{
  *PTR_0010cec0 = 0;
  *PTR_0010cec8 = 0;
  *PTR_0010ced0 = 0;
  *PTR_0010ce20 = 0;
  *PTR_0010ce28 = 0;
  *PTR_0010ced8 = 0;
  *PTR_0010cee0 = 0;
  *PTR_0010ce48 = 0;
  *PTR_0010cea8 = 0;
  *PTR_0010ce60 = 0;
  *PTR_0010ce68 = 0;
  *PTR_0010ce88 = 0;
  return;
}



// === x2com_stop_resp_timer at 00105b60 (115 bytes) ===

void x2com_stop_resp_timer(long *param_1,undefined8 param_2)

{
  long lVar1;
  long lVar2;
  
  lVar1 = (**(code **)(*param_1 + 0x30))
                    (param_1,"com/quadzillapower/iQuad/bluetooth/BluetoothChatService");
  if (lVar1 != 0) {
    lVar2 = (**(code **)(*param_1 + 0x108))(param_1,lVar1,"btsStopRespTimer",&DAT_00109478);
    if (lVar2 != 0) {
      (**(code **)(*param_1 + 0x1e8))(param_1,param_2,lVar2);
                    /* WARNING: Could not recover jumptable at 0x00105bcb. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      (**(code **)(*param_1 + 0xb8))(param_1,lVar1);
      return;
    }
  }
  return;
}



// === x2com_stop_ack_timer at 00105be0 (115 bytes) ===

void x2com_stop_ack_timer(long *param_1,undefined8 param_2)

{
  long lVar1;
  long lVar2;
  
  lVar1 = (**(code **)(*param_1 + 0x30))
                    (param_1,"com/quadzillapower/iQuad/bluetooth/BluetoothChatService");
  if (lVar1 != 0) {
    lVar2 = (**(code **)(*param_1 + 0x108))(param_1,lVar1,"btsStopAckTimer",&DAT_00109478);
    if (lVar2 != 0) {
      (**(code **)(*param_1 + 0x1e8))(param_1,param_2,lVar2);
                    /* WARNING: Could not recover jumptable at 0x00105c4b. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      (**(code **)(*param_1 + 0xb8))(param_1,lVar1);
      return;
    }
  }
  return;
}



// === x2com_start_resp_timer at 00105c60 (115 bytes) ===

void x2com_start_resp_timer(long *param_1,undefined8 param_2)

{
  long lVar1;
  long lVar2;
  
  lVar1 = (**(code **)(*param_1 + 0x30))
                    (param_1,"com/quadzillapower/iQuad/bluetooth/BluetoothChatService");
  if (lVar1 != 0) {
    lVar2 = (**(code **)(*param_1 + 0x108))(param_1,lVar1,"btsStartRespTimer",&DAT_00109478);
    if (lVar2 != 0) {
      (**(code **)(*param_1 + 0x1e8))(param_1,param_2,lVar2);
                    /* WARNING: Could not recover jumptable at 0x00105ccb. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      (**(code **)(*param_1 + 0xb8))(param_1,lVar1);
      return;
    }
  }
  return;
}



// === x2com_start_ack_timer at 00105ce0 (115 bytes) ===

void x2com_start_ack_timer(long *param_1,undefined8 param_2)

{
  long lVar1;
  long lVar2;
  
  lVar1 = (**(code **)(*param_1 + 0x30))
                    (param_1,"com/quadzillapower/iQuad/bluetooth/BluetoothChatService");
  if (lVar1 != 0) {
    lVar2 = (**(code **)(*param_1 + 0x108))(param_1,lVar1,"btsStartAckTimer",&DAT_00109478);
    if (lVar2 != 0) {
      (**(code **)(*param_1 + 0x1e8))(param_1,param_2,lVar2);
                    /* WARNING: Could not recover jumptable at 0x00105d4b. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      (**(code **)(*param_1 + 0xb8))(param_1,lVar1);
      return;
    }
  }
  return;
}



// === x2com_build_msg at 001066c0 (86 bytes) ===

int x2com_build_msg(byte *param_1,undefined8 param_2,undefined8 param_3,char *param_4)

{
  char cVar1;
  byte bVar2;
  byte bVar3;
  
  *param_1 = (char)param_2 << 4 | *param_1 & 0xf;
  cVar1 = x2com_set_msg_data(param_1 + 1,param_2,param_3,param_4);
  bVar2 = cVar1 + 1;
  *param_1 = *param_1 & 0xf0 | bVar2 & 0xf;
  bVar3 = x2com_generate_crc(param_1,(ulong)bVar2);
  param_1[bVar2] = bVar3;
  return 2 - (uint)(*param_4 == '\0');
}



// === Java_com_quadzillapower_iQuad_bluetooth_BluetoothChatService_X2comHandleResp at 00107420 (53 bytes) ===

void Java_com_quadzillapower_iQuad_bluetooth_BluetoothChatService_X2comHandleResp(void)

{
  *PTR_0010ce80 = 1;
  *PTR_0010ce88 = 0;
  if (*PTR_0010ce90 != '\0') {
    *PTR_0010ce98 = 1;
    *PTR_0010ce68 = 0;
  }
  return;
}



// === x2com_handle_resp_timeout at 00107460 (53 bytes) ===

void x2com_handle_resp_timeout(void)

{
  *PTR_0010ce80 = 1;
  *PTR_0010ce88 = 0;
  if (*PTR_0010ce90 != '\0') {
    *PTR_0010ce98 = 1;
    *PTR_0010ce68 = 0;
  }
  return;
}



// === Java_com_quadzillapower_iQuad_bluetooth_BluetoothChatService_X2comHandleAck at 001074a0 (53 bytes) ===

void Java_com_quadzillapower_iQuad_bluetooth_BluetoothChatService_X2comHandleAck(void)

{
  *PTR_0010cea0 = 1;
  *PTR_0010cea8 = 0;
  if (*PTR_0010ceb0 != '\0') {
    *PTR_0010ceb8 = 1;
    *PTR_0010ce48 = 0;
  }
  return;
}



// === x2com_handle_ack_timeout at 001074e0 (53 bytes) ===

void x2com_handle_ack_timeout(void)

{
  *PTR_0010cea0 = 1;
  *PTR_0010cea8 = 0;
  if (*PTR_0010ceb0 != '\0') {
    *PTR_0010ceb8 = 1;
    *PTR_0010ce48 = 0;
  }
  return;
}



// === x2com_get_data_size at 00105f80 (41 bytes) ===

undefined1 x2com_get_data_size(undefined1 param_1,byte param_2)

{
  undefined1 uVar1;
  
  uVar1 = 1;
  if ((((0x4a < param_2) && (uVar1 = 2, 0x95 < param_2)) && (uVar1 = 3, 0xb8 < param_2)) &&
     (uVar1 = 4, 0xdb < param_2)) {
    uVar1 = param_1;
  }
  return uVar1;
}



// === x2com_check_crc at 00105f20 (30 bytes) ===

int x2com_check_crc(undefined8 param_1,char param_2)

{
  char cVar1;
  
  cVar1 = x2com_generate_crc(param_1,param_2 + '\x01');
  return 4 - (uint)(cVar1 == ';');
}



// === x2com_set_msg_type at 00105f50 (15 bytes) ===

void x2com_set_msg_type(byte *param_1,char param_2)

{
  *param_1 = param_2 << 4 | *param_1 & 0xf;
  return;
}



// === x2com_set_msg_last_pos at 00105f70 (14 bytes) ===

void x2com_set_msg_last_pos(byte *param_1,byte param_2)

{
  *param_1 = *param_1 & 0xf0 | param_2 & 0xf;
  return;
}



// === x2com_get_msg_type at 00105f40 (7 bytes) ===

byte x2com_get_msg_type(byte *param_1)

{
  return *param_1 >> 4;
}



// === x2com_generate_crc at 00105630 (6 bytes) ===

/* WARNING: Switch with 1 destination removed at 0x00105630 */

byte x2com_generate_crc(long param_1,char param_2)

{
  byte bVar1;
  byte bVar2;
  byte bVar3;
  long lVar4;
  
  if (param_2 == '\0') {
    return 0;
  }
  bVar3 = 0xff;
  lVar4 = 0;
  do {
    bVar1 = *(byte *)(param_1 + lVar4);
    if ((char)bVar1 < '\0') {
      bVar2 = 0x1c;
      if ((char)bVar3 < '\0') {
        bVar2 = 1;
      }
      bVar2 = (bVar3 * '\x02' | 1) ^ bVar2;
      if ((bVar1 & 0x40) == 0) goto LAB_00105dbb;
LAB_00105e7b:
      bVar3 = 0x1c;
      if ((char)bVar2 < '\0') {
        bVar3 = 1;
      }
      bVar3 = (bVar2 * '\x02' | 1) ^ bVar3;
      if ((bVar1 & 0x20) != 0) goto LAB_00105dd0;
LAB_00105e95:
      bVar2 = bVar3 * '\x02' ^ (char)bVar3 >> 7 & 0x1dU;
      if ((bVar1 & 0x10) != 0) goto LAB_00105dea;
LAB_00105eaa:
      bVar3 = bVar2 * '\x02' ^ (char)bVar2 >> 7 & 0x1dU;
      if ((bVar1 & 8) != 0) goto LAB_00105e04;
LAB_00105ebf:
      bVar2 = bVar3 * '\x02' ^ (char)bVar3 >> 7 & 0x1dU;
      if ((bVar1 & 4) != 0) goto LAB_00105e1e;
LAB_00105ed4:
      bVar3 = bVar2 * '\x02' ^ (char)bVar2 >> 7 & 0x1dU;
      if ((bVar1 & 2) != 0) goto LAB_00105e38;
LAB_00105ee9:
      bVar2 = bVar3 * '\x02' ^ (char)bVar3 >> 7 & 0x1dU;
      if ((bVar1 & 1) != 0) goto LAB_00105efe;
LAB_00105d80:
      bVar3 = bVar2 * '\x02' ^ (char)bVar2 >> 7 & 0x1dU;
    }
    else {
      bVar2 = bVar3 * '\x02' ^ (char)bVar3 >> 7 & 0x1dU;
      if ((bVar1 & 0x40) != 0) goto LAB_00105e7b;
LAB_00105dbb:
      bVar3 = bVar2 * '\x02' ^ (char)bVar2 >> 7 & 0x1dU;
      if ((bVar1 & 0x20) == 0) goto LAB_00105e95;
LAB_00105dd0:
      bVar2 = 0x1c;
      if ((char)bVar3 < '\0') {
        bVar2 = 1;
      }
      bVar2 = (bVar3 * '\x02' | 1) ^ bVar2;
      if ((bVar1 & 0x10) == 0) goto LAB_00105eaa;
LAB_00105dea:
      bVar3 = 0x1c;
      if ((char)bVar2 < '\0') {
        bVar3 = 1;
      }
      bVar3 = (bVar2 * '\x02' | 1) ^ bVar3;
      if ((bVar1 & 8) == 0) goto LAB_00105ebf;
LAB_00105e04:
      bVar2 = 0x1c;
      if ((char)bVar3 < '\0') {
        bVar2 = 1;
      }
      bVar2 = (bVar3 * '\x02' | 1) ^ bVar2;
      if ((bVar1 & 4) == 0) goto LAB_00105ed4;
LAB_00105e1e:
      bVar3 = 0x1c;
      if ((char)bVar2 < '\0') {
        bVar3 = 1;
      }
      bVar3 = (bVar2 * '\x02' | 1) ^ bVar3;
      if ((bVar1 & 2) == 0) goto LAB_00105ee9;
LAB_00105e38:
      bVar2 = 0x1c;
      if ((char)bVar3 < '\0') {
        bVar2 = 1;
      }
      bVar2 = (bVar3 * '\x02' | 1) ^ bVar2;
      if ((bVar1 & 1) == 0) goto LAB_00105d80;
LAB_00105efe:
      bVar3 = 0x1c;
      if ((char)bVar2 < '\0') {
        bVar3 = 1;
      }
      bVar3 = (bVar2 * '\x02' | 1) ^ bVar3;
    }
    lVar4 = lVar4 + 1;
    if (param_2 == (char)lVar4) {
      return ~bVar3;
    }
  } while( true );
}



// === x2com_get_msg_data at 00105660 (6 bytes) ===

/* WARNING: Switch with 1 destination removed at 0x00105660 */

int x2com_get_msg_data(byte *param_1,byte param_2,int param_3,byte *param_4,char *param_5)

{
  byte bVar1;
  undefined *puVar2;
  undefined *puVar3;
  ulong uVar4;
  byte bVar5;
  undefined8 *puVar6;
  char cVar7;
  byte bVar8;
  byte unaff_R12B;
  char cVar9;
  byte *unaff_R15;
  
  puVar3 = PTR_two_byte_rx_p_0010cdd8;
  puVar2 = PTR_one_byte_rx_p_0010cdd0;
  bVar8 = 0xe;
  if (param_2 < 0xe) {
    bVar8 = param_2;
  }
  if (bVar8 == 0) {
    cVar7 = '\0';
LAB_0010621e:
    *param_5 = cVar7;
    return 2 - (uint)(unaff_R12B == 0);
  }
  cVar9 = '\x01';
  cVar7 = '\0';
  bVar5 = 0;
  if (param_3 != 4) goto LAB_00106141;
  do {
    bVar1 = *param_1;
    param_1 = param_1 + 1;
    *param_4 = bVar1;
    param_4 = param_4 + 1;
    cVar7 = cVar7 + '\x01';
    while( true ) {
      bVar5 = bVar5 + 1;
      if (bVar8 <= bVar5) goto LAB_0010621e;
      if (param_3 == 4) break;
LAB_00106141:
      if (param_3 == 2) break;
      if (cVar9 == '\x02') {
        bVar1 = *param_1;
        param_1 = param_1 + 1;
        *unaff_R15 = bVar1;
        unaff_R15 = unaff_R15 + 1;
        unaff_R12B = unaff_R12B - 1;
        cVar9 = '\x02' - (unaff_R12B == 0);
      }
      else if (cVar9 == '\x01') {
        bVar1 = *param_1;
        uVar4 = (ulong)bVar1;
        if (uVar4 < 0x4b) {
          puVar6 = (undefined8 *)(puVar2 + uVar4 * 8);
          unaff_R12B = 1;
        }
        else if (bVar1 < 0x96) {
          puVar6 = (undefined8 *)(puVar3 + uVar4 * 8 + -600);
          unaff_R12B = 2;
        }
        else if (bVar1 < 0xb9) {
          puVar6 = (undefined8 *)(PTR_three_byte_rx_p_0010cde0 + uVar4 * 8 + -0x4b0);
          unaff_R12B = 3;
        }
        else if (bVar1 < 0xdc) {
          puVar6 = (undefined8 *)(PTR_four_byte_rx_p_0010cde8 + uVar4 * 8 + -0x5c8);
          unaff_R12B = 4;
        }
        else {
          unaff_R12B = param_1[1];
          puVar6 = (undefined8 *)(PTR_var_byte_rx_p_0010cdf0 + uVar4 * 8 + -0x6e0);
        }
        param_1 = param_1 + 1;
        unaff_R15 = (byte *)*puVar6;
        if (unaff_R15 == (byte *)0x0) {
          unaff_R15 = (byte *)0x0;
          cVar9 = '\0';
        }
        else {
          *param_4 = bVar1;
          param_4 = param_4 + 1;
          cVar7 = cVar7 + '\x01';
          cVar9 = '\x02';
        }
      }
      else {
        param_1 = param_1 + 1;
        unaff_R12B = unaff_R12B - 1;
        if (unaff_R12B == 0) {
          cVar9 = '\x01';
        }
      }
    }
  } while( true );
}



// === x2com_set_msg_data at 00105670 (6 bytes) ===

/* WARNING: Switch with 1 destination removed at 0x00105670 */

byte x2com_set_msg_data(byte *param_1,int param_2,byte *param_3,char *param_4)

{
  byte bVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  ulong uVar5;
  char cVar6;
  undefined *puVar7;
  long lVar8;
  long lVar9;
  ulong uVar10;
  undefined8 *puVar11;
  byte *pbVar12;
  uint uVar13;
  byte *pbVar14;
  byte bVar15;
  char cVar16;
  byte bVar17;
  byte bVar18;
  ulong uVar19;
  byte *pbVar20;
  ulong uVar21;
  byte bVar22;
  long in_FS_OFFSET;
  byte abStack_46 [14];
  long lStack_38;
  
  lStack_38 = *(long *)(in_FS_OFFSET + 0x28);
  cVar16 = *param_4;
  uVar13 = 0;
  if (cVar16 == '\0') {
    cVar16 = '\0';
    bVar22 = 0;
  }
  else {
    uVar19 = 0;
    bVar22 = 0;
    puVar7 = PTR_one_byte_tx_p_0010cdf8;
    pbVar20 = param_3;
    do {
      bVar17 = *pbVar20;
      if ((param_2 == 4) || (param_2 == 2)) {
        *param_1 = bVar17;
        bVar22 = bVar22 + 1;
        param_1 = param_1 + 1;
      }
      else {
        uVar10 = (ulong)bVar17;
        if (bVar17 < 0x4b) {
          puVar11 = (undefined8 *)(puVar7 + uVar10 * 8);
        }
        else if (bVar17 < 0x96) {
          puVar11 = (undefined8 *)(PTR_two_byte_tx_p_0010ce00 + uVar10 * 8 + -600);
        }
        else if (bVar17 < 0xb9) {
          puVar11 = (undefined8 *)(PTR_three_byte_tx_p_0010ce08 + uVar10 * 8 + -0x4b0);
        }
        else if (bVar17 < 0xdc) {
          puVar11 = (undefined8 *)(PTR_four_byte_tx_p_0010ce10 + uVar10 * 8 + -0x5c8);
        }
        else {
          puVar11 = (undefined8 *)(PTR_var_byte_tx_p_0010ce18 + uVar10 * 8 + -0x6e0);
        }
        pbVar12 = (byte *)*puVar11;
        uVar10 = uVar19 & 0xff;
        if (pbVar12 != (byte *)0x0) {
          bVar15 = 1;
          if ((((0x4a < bVar17) && (bVar15 = 2, 0x95 < bVar17)) && (bVar15 = 3, 0xb8 < bVar17)) &&
             (bVar15 = *pbVar12, bVar17 < 0xdc)) {
            bVar15 = 4;
          }
          if (uVar13 + bVar15 < 0xe) {
            *param_1 = bVar17;
            pbVar14 = param_1 + 1;
            if (bVar15 == 0) {
              bVar22 = bVar22 + 1;
              param_1 = pbVar14;
              goto joined_r0x001065b5;
            }
            uVar5 = (ulong)(byte)(bVar15 - 1);
            uVar10 = uVar5 + 1;
            if (uVar10 < 0x20) {
              bVar17 = 0;
LAB_001064f6:
              bVar18 = ~bVar17;
              if ((bVar15 & 7) != 0) {
                cVar6 = '\0';
                do {
                  bVar1 = *pbVar12;
                  pbVar12 = pbVar12 + 1;
                  *pbVar14 = bVar1;
                  pbVar14 = pbVar14 + 1;
                  cVar6 = cVar6 + -1;
                } while (-(bVar15 & 7) != cVar6);
                bVar17 = bVar17 - cVar6;
                puVar7 = PTR_one_byte_tx_p_0010cdf8;
              }
              if (6 < (byte)(bVar18 + bVar15)) {
                lVar8 = 0;
                do {
                  pbVar14[lVar8] = pbVar12[lVar8];
                  pbVar14[lVar8 + 1] = pbVar12[lVar8 + 1];
                  pbVar14[lVar8 + 2] = pbVar12[lVar8 + 2];
                  pbVar14[lVar8 + 3] = pbVar12[lVar8 + 3];
                  pbVar14[lVar8 + 4] = pbVar12[lVar8 + 4];
                  pbVar14[lVar8 + 5] = pbVar12[lVar8 + 5];
                  pbVar14[lVar8 + 6] = pbVar12[lVar8 + 6];
                  pbVar14[lVar8 + 7] = pbVar12[lVar8 + 7];
                  lVar8 = lVar8 + 8;
                } while ((byte)(bVar15 - bVar17) != (char)lVar8);
                pbVar14 = pbVar14 + lVar8;
                puVar7 = PTR_one_byte_tx_p_0010cdf8;
              }
            }
            else {
              if ((pbVar14 < pbVar12 + uVar5 + 1) && (pbVar12 < param_1 + uVar5 + 2)) {
                uVar13 = 0;
LAB_001064ef:
                bVar17 = (byte)uVar13;
                puVar7 = PTR_one_byte_tx_p_0010cdf8;
                goto LAB_001064f6;
              }
              uVar13 = (uint)uVar10 & 0xffffffe0;
              uVar5 = (ulong)uVar13;
              lVar8 = (uVar5 - 0x20 >> 5) + 1;
              uVar21 = (ulong)((uint)lVar8 & 3);
              if (uVar5 - 0x20 < 0x60) {
                lVar9 = 0;
              }
              else {
                lVar8 = uVar21 - lVar8;
                lVar9 = 0;
                do {
                  uVar2 = *(undefined8 *)(pbVar12 + lVar9 + 8);
                  uVar3 = *(undefined8 *)(pbVar12 + lVar9 + 0x10);
                  uVar4 = *(undefined8 *)(pbVar12 + lVar9 + 0x10 + 8);
                  *(undefined8 *)(param_1 + lVar9 + 1) = *(undefined8 *)(pbVar12 + lVar9);
                  *(undefined8 *)(param_1 + lVar9 + 1 + 8) = uVar2;
                  *(undefined8 *)(param_1 + lVar9 + 0x11) = uVar3;
                  *(undefined8 *)(param_1 + lVar9 + 0x11 + 8) = uVar4;
                  uVar2 = *(undefined8 *)(pbVar12 + lVar9 + 0x20 + 8);
                  uVar3 = *(undefined8 *)(pbVar12 + lVar9 + 0x30);
                  uVar4 = *(undefined8 *)(pbVar12 + lVar9 + 0x30 + 8);
                  *(undefined8 *)(param_1 + lVar9 + 0x21) = *(undefined8 *)(pbVar12 + lVar9 + 0x20);
                  *(undefined8 *)(param_1 + lVar9 + 0x21 + 8) = uVar2;
                  *(undefined8 *)(param_1 + lVar9 + 0x31) = uVar3;
                  *(undefined8 *)(param_1 + lVar9 + 0x31 + 8) = uVar4;
                  uVar2 = *(undefined8 *)(pbVar12 + lVar9 + 0x40 + 8);
                  uVar3 = *(undefined8 *)(pbVar12 + lVar9 + 0x50);
                  uVar4 = *(undefined8 *)(pbVar12 + lVar9 + 0x50 + 8);
                  *(undefined8 *)(param_1 + lVar9 + 0x41) = *(undefined8 *)(pbVar12 + lVar9 + 0x40);
                  *(undefined8 *)(param_1 + lVar9 + 0x41 + 8) = uVar2;
                  *(undefined8 *)(param_1 + lVar9 + 0x51) = uVar3;
                  *(undefined8 *)(param_1 + lVar9 + 0x51 + 8) = uVar4;
                  uVar2 = *(undefined8 *)(pbVar12 + lVar9 + 0x60 + 8);
                  uVar3 = *(undefined8 *)(pbVar12 + lVar9 + 0x70);
                  uVar4 = *(undefined8 *)(pbVar12 + lVar9 + 0x70 + 8);
                  *(undefined8 *)(param_1 + lVar9 + 0x61) = *(undefined8 *)(pbVar12 + lVar9 + 0x60);
                  *(undefined8 *)(param_1 + lVar9 + 0x61 + 8) = uVar2;
                  *(undefined8 *)(param_1 + lVar9 + 0x71) = uVar3;
                  *(undefined8 *)(param_1 + lVar9 + 0x71 + 8) = uVar4;
                  lVar9 = lVar9 + 0x80;
                  lVar8 = lVar8 + 4;
                } while (lVar8 != 0);
              }
              if (uVar21 != 0) {
                lVar8 = 0;
                do {
                  uVar2 = *(undefined8 *)(pbVar12 + lVar8 + lVar9 + 8);
                  uVar3 = *(undefined8 *)(pbVar12 + lVar8 + lVar9 + 0x10);
                  uVar4 = *(undefined8 *)(pbVar12 + lVar8 + lVar9 + 0x10 + 8);
                  *(undefined8 *)(param_1 + lVar8 + lVar9 + 1) =
                       *(undefined8 *)(pbVar12 + lVar8 + lVar9);
                  *(undefined8 *)(param_1 + lVar8 + lVar9 + 1 + 8) = uVar2;
                  *(undefined8 *)(param_1 + lVar8 + lVar9 + 0x11) = uVar3;
                  *(undefined8 *)(param_1 + lVar8 + lVar9 + 0x11 + 8) = uVar4;
                  lVar8 = lVar8 + 0x20;
                } while (uVar21 << 5 != lVar8);
              }
              pbVar14 = pbVar14 + uVar5;
              puVar7 = PTR_one_byte_tx_p_0010cdf8;
              if (uVar10 != uVar5) {
                pbVar12 = pbVar12 + uVar5;
                goto LAB_001064ef;
              }
            }
            bVar22 = bVar22 + bVar15 + 1;
            param_1 = pbVar14;
            goto joined_r0x001065b5;
          }
        }
        uVar19 = (ulong)((int)uVar10 + 1);
        abStack_46[uVar10] = bVar17;
      }
joined_r0x001065b5:
      if (0xd < bVar22) break;
      cVar16 = cVar16 + -1;
      pbVar20 = pbVar20 + 1;
      uVar13 = (uint)bVar22;
    } while (cVar16 != '\0');
    cVar16 = (char)uVar19;
    if (cVar16 == '\0') {
      cVar16 = '\0';
    }
    else {
      memcpy(param_3,abStack_46,uVar19 & 0xff);
    }
  }
  *param_4 = cVar16;
  if (*(long *)(in_FS_OFFSET + 0x28) == lStack_38) {
    return bVar22;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



// === x2com_rcv at 00105690 (6 bytes) ===

/* WARNING: Switch with 1 destination removed at 0x00105690 */

int x2com_rcv(undefined8 param_1,undefined8 param_2,undefined *param_3,byte *param_4)

{
  char cVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined1 uVar5;
  int iVar6;
  undefined1 *puVar7;
  byte bVar8;
  uint uVar9;
  long lVar10;
  byte bVar11;
  ulong uVar12;
  ulong uVar13;
  undefined *puVar14;
  ulong uVar15;
  undefined *puVar16;
  long lVar17;
  byte bVar18;
  byte *pbVar19;
  long in_FS_OFFSET;
  undefined4 uStack_4c;
  char acStack_46 [14];
  long lStack_38;
  
  lStack_38 = *(long *)(in_FS_OFFSET + 0x28);
  uVar5 = x2com_get_msg_last_pos(param_3);
  iVar6 = x2com_check_crc(param_3,uVar5);
  if (iVar6 != 3) goto switchD_00107762_default;
  uStack_4c = x2com_get_msg_type(param_3);
  puVar14 = PTR_0010ce68;
  iVar6 = 3;
  switch(uStack_4c) {
  case 0:
    iVar6 = x2com_parse_msg(param_3,&uStack_4c,param_3,param_4);
    puVar14 = PTR_0010cef8;
    bVar11 = *param_4;
    if (bVar11 == 0) goto switchD_00107762_default;
    bVar18 = 0xe;
    if (bVar11 < 0xe) {
      bVar18 = bVar11;
    }
    if (bVar18 != 0) {
      uVar13 = (ulong)(byte)(bVar18 - 1);
      uVar15 = uVar13 + 1;
      if ((uVar15 < 0x20) ||
         ((PTR_0010cef8 < param_3 + uVar13 + 1 && (param_3 < PTR_0010cef8 + uVar13 + 1)))) {
        uVar9 = 0;
      }
      else {
        uVar9 = (uint)uVar15 & 0xffffffe0;
        uVar13 = (ulong)uVar9;
        lVar10 = (uVar13 - 0x20 >> 5) + 1;
        uVar12 = (ulong)((uint)lVar10 & 3);
        if (uVar13 - 0x20 < 0x60) {
          lVar17 = 0;
          puVar16 = PTR_0010cef8;
        }
        else {
          lVar10 = uVar12 - lVar10;
          lVar17 = 0;
          do {
            uVar2 = *(undefined8 *)((long)(param_3 + lVar17) + 8);
            uVar3 = *(undefined8 *)(param_3 + lVar17 + 0x10);
            uVar4 = *(undefined8 *)((long)(param_3 + lVar17 + 0x10) + 8);
            *(undefined8 *)(puVar14 + lVar17) = *(undefined8 *)(param_3 + lVar17);
            *(undefined8 *)((long)(puVar14 + lVar17) + 8) = uVar2;
            *(undefined8 *)(puVar14 + lVar17 + 0x10) = uVar3;
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x10) + 8) = uVar4;
            uVar2 = *(undefined8 *)((long)(param_3 + lVar17 + 0x20) + 8);
            uVar3 = *(undefined8 *)(param_3 + lVar17 + 0x30);
            uVar4 = *(undefined8 *)((long)(param_3 + lVar17 + 0x30) + 8);
            *(undefined8 *)(puVar14 + lVar17 + 0x20) = *(undefined8 *)(param_3 + lVar17 + 0x20);
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x20) + 8) = uVar2;
            *(undefined8 *)(puVar14 + lVar17 + 0x30) = uVar3;
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x30) + 8) = uVar4;
            uVar2 = *(undefined8 *)((long)(param_3 + lVar17 + 0x40) + 8);
            uVar3 = *(undefined8 *)(param_3 + lVar17 + 0x50);
            uVar4 = *(undefined8 *)((long)(param_3 + lVar17 + 0x50) + 8);
            *(undefined8 *)(puVar14 + lVar17 + 0x40) = *(undefined8 *)(param_3 + lVar17 + 0x40);
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x40) + 8) = uVar2;
            *(undefined8 *)(puVar14 + lVar17 + 0x50) = uVar3;
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x50) + 8) = uVar4;
            uVar2 = *(undefined8 *)((long)(param_3 + lVar17 + 0x60) + 8);
            uVar3 = *(undefined8 *)(param_3 + lVar17 + 0x70);
            uVar4 = *(undefined8 *)((long)(param_3 + lVar17 + 0x70) + 8);
            *(undefined8 *)(puVar14 + lVar17 + 0x60) = *(undefined8 *)(param_3 + lVar17 + 0x60);
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x60) + 8) = uVar2;
            *(undefined8 *)(puVar14 + lVar17 + 0x70) = uVar3;
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x70) + 8) = uVar4;
            lVar17 = lVar17 + 0x80;
            lVar10 = lVar10 + 4;
            puVar16 = PTR_0010cef8;
          } while (lVar10 != 0);
        }
        PTR_0010cef8 = puVar16;
        if (uVar12 != 0) {
          lVar17 = lVar17 + 0x10;
          lVar10 = -uVar12;
          do {
            uVar2 = *(undefined8 *)((long)(param_3 + lVar17 + -0x10) + 8);
            uVar3 = *(undefined8 *)(param_3 + lVar17);
            uVar4 = *(undefined8 *)((long)(param_3 + lVar17) + 8);
            *(undefined8 *)(puVar16 + lVar17 + -0x10) = *(undefined8 *)(param_3 + lVar17 + -0x10);
            *(undefined8 *)((long)(puVar16 + lVar17 + -0x10) + 8) = uVar2;
            *(undefined8 *)(puVar16 + lVar17) = uVar3;
            *(undefined8 *)((long)(puVar16 + lVar17) + 8) = uVar4;
            lVar17 = lVar17 + 0x20;
            lVar10 = lVar10 + 1;
          } while (lVar10 != 0);
        }
        if (uVar15 == uVar13) goto LAB_001078e3;
        param_3 = param_3 + uVar13;
        puVar14 = PTR_0010cef8 + uVar13;
      }
      lVar10 = 0;
      do {
        puVar14[lVar10] = param_3[lVar10];
        lVar10 = lVar10 + 1;
      } while ((byte)((char)uVar9 + (char)lVar10) < bVar18);
    }
LAB_001078e3:
    *PTR_0010cf00 = bVar18;
    puVar7 = PTR_0010ced0;
    break;
  case 1:
  case 3:
    iVar6 = x2com_parse_msg(param_3,&uStack_4c,param_3,param_4);
    goto switchD_00107762_default;
  case 2:
    __android_log_print(6,"BluetoothChatService","x2com_rcv - X2COM_ACK");
    puVar14 = PTR_0010cea8;
    if ((*PTR_0010ce48 == '\0') || (*PTR_0010cea8 == '\0')) goto switchD_00107762_default;
    iVar6 = x2com_parse_msg(param_3,&uStack_4c,param_3,param_4);
    bVar11 = *param_4;
    if ((bVar11 != 0) && (bVar18 = *PTR_0010cee8, (ulong)bVar18 != 0)) {
      bVar8 = 0xe;
      if (bVar11 < 0xe) {
        bVar8 = bVar11;
      }
      uVar15 = 0;
      bVar11 = 0;
      do {
        cVar1 = PTR_0010cef0[uVar15];
        uVar13 = 1;
        do {
          lVar10 = uVar13 - 1;
          if (bVar8 <= uVar13) break;
          uVar13 = uVar13 + 1;
        } while (cVar1 != param_3[lVar10]);
        if (cVar1 != param_3[lVar10]) {
          uVar13 = (ulong)bVar11;
          bVar11 = bVar11 + 1;
          acStack_46[uVar13] = cVar1;
        }
        uVar15 = uVar15 + 1;
      } while (uVar15 != bVar18);
      puVar16 = PTR_0010cef0;
      pbVar19 = PTR_0010cee8;
      if (bVar11 != 0) {
LAB_00107b0b:
        memcpy(puVar16,acStack_46,(ulong)bVar11);
        *pbVar19 = bVar11;
        goto switchD_00107762_default;
      }
    }
    *PTR_0010cee8 = 0;
    *puVar14 = 0;
    x2com_stop_ack_timer(param_1,param_2);
    if (*PTR_0010ceb0 == '\0') goto switchD_00107762_default;
    __android_log_print(6,"BluetoothChatService","x2com_rcv - X2COM_ACK_RCVD");
    *PTR_0010ce48 = 0;
    iVar6 = 7;
    cVar1 = *PTR_0010cea0;
    puVar7 = PTR_0010ceb8;
    goto joined_r0x00107b64;
  case 4:
    iVar6 = x2com_parse_msg(param_3,&uStack_4c,param_3,param_4);
    puVar14 = PTR_0010cf18;
    bVar11 = *param_4;
    if (bVar11 == 0) goto switchD_00107762_default;
    bVar18 = 0xe;
    if (bVar11 < 0xe) {
      bVar18 = bVar11;
    }
    if (bVar18 != 0) {
      uVar13 = (ulong)(byte)(bVar18 - 1);
      uVar15 = uVar13 + 1;
      if ((uVar15 < 0x20) ||
         ((PTR_0010cf18 < param_3 + uVar13 + 1 && (param_3 < PTR_0010cf18 + uVar13 + 1)))) {
        uVar9 = 0;
      }
      else {
        uVar9 = (uint)uVar15 & 0xffffffe0;
        uVar13 = (ulong)uVar9;
        lVar10 = (uVar13 - 0x20 >> 5) + 1;
        uVar12 = (ulong)((uint)lVar10 & 3);
        if (uVar13 - 0x20 < 0x60) {
          lVar17 = 0;
          puVar16 = PTR_0010cf18;
        }
        else {
          lVar10 = uVar12 - lVar10;
          lVar17 = 0;
          do {
            uVar2 = *(undefined8 *)((long)(param_3 + lVar17) + 8);
            uVar3 = *(undefined8 *)(param_3 + lVar17 + 0x10);
            uVar4 = *(undefined8 *)((long)(param_3 + lVar17 + 0x10) + 8);
            *(undefined8 *)(puVar14 + lVar17) = *(undefined8 *)(param_3 + lVar17);
            *(undefined8 *)((long)(puVar14 + lVar17) + 8) = uVar2;
            *(undefined8 *)(puVar14 + lVar17 + 0x10) = uVar3;
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x10) + 8) = uVar4;
            uVar2 = *(undefined8 *)((long)(param_3 + lVar17 + 0x20) + 8);
            uVar3 = *(undefined8 *)(param_3 + lVar17 + 0x30);
            uVar4 = *(undefined8 *)((long)(param_3 + lVar17 + 0x30) + 8);
            *(undefined8 *)(puVar14 + lVar17 + 0x20) = *(undefined8 *)(param_3 + lVar17 + 0x20);
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x20) + 8) = uVar2;
            *(undefined8 *)(puVar14 + lVar17 + 0x30) = uVar3;
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x30) + 8) = uVar4;
            uVar2 = *(undefined8 *)((long)(param_3 + lVar17 + 0x40) + 8);
            uVar3 = *(undefined8 *)(param_3 + lVar17 + 0x50);
            uVar4 = *(undefined8 *)((long)(param_3 + lVar17 + 0x50) + 8);
            *(undefined8 *)(puVar14 + lVar17 + 0x40) = *(undefined8 *)(param_3 + lVar17 + 0x40);
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x40) + 8) = uVar2;
            *(undefined8 *)(puVar14 + lVar17 + 0x50) = uVar3;
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x50) + 8) = uVar4;
            uVar2 = *(undefined8 *)((long)(param_3 + lVar17 + 0x60) + 8);
            uVar3 = *(undefined8 *)(param_3 + lVar17 + 0x70);
            uVar4 = *(undefined8 *)((long)(param_3 + lVar17 + 0x70) + 8);
            *(undefined8 *)(puVar14 + lVar17 + 0x60) = *(undefined8 *)(param_3 + lVar17 + 0x60);
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x60) + 8) = uVar2;
            *(undefined8 *)(puVar14 + lVar17 + 0x70) = uVar3;
            *(undefined8 *)((long)(puVar14 + lVar17 + 0x70) + 8) = uVar4;
            lVar17 = lVar17 + 0x80;
            lVar10 = lVar10 + 4;
            puVar16 = PTR_0010cf18;
          } while (lVar10 != 0);
        }
        PTR_0010cf18 = puVar16;
        if (uVar12 != 0) {
          lVar17 = lVar17 + 0x10;
          lVar10 = -uVar12;
          do {
            uVar2 = *(undefined8 *)((long)(param_3 + lVar17 + -0x10) + 8);
            uVar3 = *(undefined8 *)(param_3 + lVar17);
            uVar4 = *(undefined8 *)((long)(param_3 + lVar17) + 8);
            *(undefined8 *)(puVar16 + lVar17 + -0x10) = *(undefined8 *)(param_3 + lVar17 + -0x10);
            *(undefined8 *)((long)(puVar16 + lVar17 + -0x10) + 8) = uVar2;
            *(undefined8 *)(puVar16 + lVar17) = uVar3;
            *(undefined8 *)((long)(puVar16 + lVar17) + 8) = uVar4;
            lVar17 = lVar17 + 0x20;
            lVar10 = lVar10 + 1;
          } while (lVar10 != 0);
        }
        if (uVar15 == uVar13) goto LAB_00107a43;
        param_3 = param_3 + uVar13;
        puVar14 = PTR_0010cf18 + uVar13;
      }
      lVar10 = 0;
      do {
        puVar14[lVar10] = param_3[lVar10];
        lVar10 = lVar10 + 1;
      } while ((byte)((char)uVar9 + (char)lVar10) < bVar18);
    }
LAB_00107a43:
    *PTR_0010cf20 = bVar18;
    puVar7 = PTR_0010cec0;
    break;
  case 5:
    if ((*PTR_0010ce68 == '\0') || (*PTR_0010ce88 == '\0')) goto switchD_00107762_default;
    iVar6 = x2com_parse_msg(param_3,&uStack_4c,param_3,param_4);
    bVar11 = *param_4;
    if ((bVar11 != 0) && (bVar18 = *PTR_0010cf08, (ulong)bVar18 != 0)) {
      bVar8 = 0xe;
      if (bVar11 < 0xe) {
        bVar8 = bVar11;
      }
      uVar15 = 0;
      bVar11 = 0;
      do {
        cVar1 = PTR_0010cf10[uVar15];
        uVar13 = 1;
        do {
          lVar10 = uVar13 - 1;
          if (bVar8 <= uVar13) break;
          uVar13 = uVar13 + 1;
        } while (cVar1 != param_3[lVar10]);
        if (cVar1 != param_3[lVar10]) {
          uVar13 = (ulong)bVar11;
          bVar11 = bVar11 + 1;
          acStack_46[uVar13] = cVar1;
        }
        uVar15 = uVar15 + 1;
      } while (uVar15 != bVar18);
      puVar16 = PTR_0010cf10;
      pbVar19 = PTR_0010cf08;
      if (bVar11 != 0) goto LAB_00107b0b;
    }
    *PTR_0010cf08 = 0;
    *PTR_0010ce88 = 0;
    x2com_stop_resp_timer(param_1,param_2);
    if (*PTR_0010ce90 == '\0') goto switchD_00107762_default;
    *puVar14 = 0;
    iVar6 = 6;
    cVar1 = *PTR_0010ce80;
    puVar7 = PTR_0010ce98;
joined_r0x00107b64:
    if (cVar1 == '\0') goto switchD_00107762_default;
    break;
  default:
    goto switchD_00107762_default;
  }
  *puVar7 = 1;
switchD_00107762_default:
  if (*(long *)(in_FS_OFFSET + 0x28) != lStack_38) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return iVar6;
}



// === x2com_get_msg_last_pos at 001056a0 (6 bytes) ===

/* WARNING: Switch with 1 destination removed at 0x001056a0 */

byte x2com_get_msg_last_pos(byte *param_1)

{
  return *param_1 & 0xf;
}



// === x2com_check_crc at 001056b0 (6 bytes) ===

/* WARNING: Switch with 1 destination removed at 0x001056b0 */

int x2com_check_crc(undefined8 param_1,char param_2)

{
  char cVar1;
  
  cVar1 = x2com_generate_crc(param_1,param_2 + '\x01');
  return 4 - (uint)(cVar1 == ';');
}



// === x2com_get_msg_type at 001056c0 (6 bytes) ===

/* WARNING: Switch with 1 destination removed at 0x001056c0 */

byte x2com_get_msg_type(byte *param_1)

{
  return *param_1 >> 4;
}



// === x2com_parse_msg at 001056d0 (6 bytes) ===

/* WARNING: Switch with 1 destination removed at 0x001056d0 */

undefined8 x2com_parse_msg(byte *param_1,uint *param_2,undefined8 param_3,undefined1 *param_4)

{
  byte bVar1;
  char cVar2;
  undefined8 uVar3;
  byte bVar4;
  uint uVar5;
  
  *param_2 = 6;
  *param_4 = 0;
  bVar1 = *param_1;
  bVar4 = bVar1 & 0xf;
  if (bVar4 == 0) {
    uVar3 = 5;
  }
  else {
    cVar2 = x2com_generate_crc(param_1,bVar4 + 1);
    uVar3 = 4;
    if (cVar2 == ';') {
      uVar5 = (uint)(bVar1 >> 4);
      *param_2 = uVar5;
      uVar3 = x2com_get_msg_data(param_1 + 1,bVar4 - 1,uVar5,param_3,param_4);
      return uVar3;
    }
  }
  return uVar3;
}



// === x2com_stop_ack_timer at 001056e0 (6 bytes) ===

/* WARNING: Switch with 1 destination removed at 0x001056e0 */

void x2com_stop_ack_timer(long *param_1,undefined8 param_2)

{
  long lVar1;
  long lVar2;
  
  lVar1 = (**(code **)(*param_1 + 0x30))
                    (param_1,"com/quadzillapower/iQuad/bluetooth/BluetoothChatService");
  if ((lVar1 != 0) &&
     (lVar2 = (**(code **)(*param_1 + 0x108))(param_1,lVar1,"btsStopAckTimer",&DAT_00109478),
     lVar2 != 0)) {
    (**(code **)(*param_1 + 0x1e8))(param_1,param_2,lVar2);
                    /* WARNING: Could not recover jumptable at 0x00105c4b. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (**(code **)(*param_1 + 0xb8))(param_1,lVar1);
    return;
  }
  return;
}



// === x2com_stop_resp_timer at 001056f0 (6 bytes) ===

/* WARNING: Switch with 1 destination removed at 0x001056f0 */

void x2com_stop_resp_timer(long *param_1,undefined8 param_2)

{
  long lVar1;
  long lVar2;
  
  lVar1 = (**(code **)(*param_1 + 0x30))
                    (param_1,"com/quadzillapower/iQuad/bluetooth/BluetoothChatService");
  if ((lVar1 != 0) &&
     (lVar2 = (**(code **)(*param_1 + 0x108))(param_1,lVar1,"btsStopRespTimer",&DAT_00109478),
     lVar2 != 0)) {
    (**(code **)(*param_1 + 0x1e8))(param_1,param_2,lVar2);
                    /* WARNING: Could not recover jumptable at 0x00105bcb. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (**(code **)(*param_1 + 0xb8))(param_1,lVar1);
    return;
  }
  return;
}



// === x2com_xmit at 00105700 (6 bytes) ===

/* WARNING: Switch with 1 destination removed at 0x00105700 */

undefined8 x2com_xmit(undefined8 param_1,undefined8 param_2)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined8 uVar6;
  undefined8 uVar7;
  undefined8 uVar8;
  undefined8 uVar9;
  undefined8 uVar10;
  undefined *puVar11;
  undefined *puVar12;
  undefined *puVar13;
  undefined *puVar14;
  undefined *puVar15;
  undefined *puVar16;
  undefined *puVar17;
  undefined *puVar18;
  undefined *puVar19;
  undefined *puVar20;
  undefined *puVar21;
  char *pcVar22;
  char cVar23;
  byte bVar24;
  uint uVar25;
  ulong uVar26;
  undefined *puVar27;
  undefined8 uVar28;
  byte bVar29;
  undefined *puVar30;
  ulong uVar31;
  undefined *puVar32;
  long lVar33;
  long lVar34;
  ulong uVar35;
  byte bVar36;
  byte bVar37;
  long in_FS_OFFSET;
  char acStack_46 [14];
  long lStack_38;
  
  lStack_38 = *(long *)(in_FS_OFFSET + 0x28);
  cVar23 = x2com_is_tx_ready();
  pcVar22 = DAT_0010cf38;
  puVar21 = PTR_0010cf28;
  puVar20 = PTR_0010cf20;
  puVar19 = PTR_0010cf10;
  puVar18 = PTR_0010cee0;
  puVar17 = PTR_0010ced0;
  puVar16 = PTR_0010cec8;
  puVar15 = PTR_0010cea8;
  puVar14 = PTR_0010ce78;
  puVar13 = PTR_0010ce70;
  puVar12 = PTR_0010ce68;
  puVar11 = PTR_0010ce48;
  puVar30 = PTR_0010ce40;
  puVar32 = PTR_0010ce38;
  puVar27 = PTR_0010ce28;
  if (cVar23 == '\0') {
    uVar28 = 8;
    goto LAB_00107eb1;
  }
  if (*PTR_0010ced0 != '\0') {
    x2com_build_msg(PTR_0010cf28,2,PTR_0010cef8,PTR_0010cf00);
    cVar23 = x2com_get_msg_last_pos(puVar21);
    x2com_tx_msg(param_1,param_2,puVar21,cVar23 + '\x01');
    *puVar17 = 0;
    uVar28 = 9;
    goto LAB_00107eb1;
  }
  if (*PTR_0010cec8 == '\0') {
    if (*PTR_0010cec0 == '\0') {
      if (*PTR_0010ce28 == '\0') {
        if (*PTR_0010ce20 == '\0') {
          if (*PTR_0010cee0 == '\0') {
            if (*PTR_0010ced8 == '\0') {
              if ((*PTR_0010cea8 == '\0' & *PTR_0010ce48) == 0) {
                if (*PTR_0010ce40 != '\0') {
                  __android_log_print(6,"BluetoothChatService","x2com_xmit - cwa needed");
                  *puVar30 = 0;
                  *PTR_0010ceb8 = 0;
                  *PTR_0010cea0 = 0;
                  *PTR_0010ceb0 = 0;
                  puVar30 = PTR_0010cef0;
                  puVar32 = PTR_0010ce58;
                  puVar27 = PTR_0010ce50;
                  bVar37 = *PTR_0010ce58;
                  if (bVar37 != 0) {
                    bVar36 = 0xe;
                    if (bVar37 < 0xe) {
                      bVar36 = bVar37;
                    }
                    if (bVar36 != 0) {
                      uVar26 = (ulong)(byte)(bVar36 - 1) + 1;
                      if (uVar26 < 0x20) {
                        uVar25 = 0;
                      }
                      else {
                        uVar25 = (uint)uVar26 & 0xffffffe0;
                        uVar35 = (ulong)uVar25;
                        lVar34 = (uVar35 - 0x20 >> 5) + 1;
                        uVar31 = (ulong)((uint)lVar34 & 1);
                        if (uVar35 - 0x20 == 0) {
                          lVar33 = 0;
                        }
                        else {
                          lVar34 = uVar31 - lVar34;
                          lVar33 = 0;
                          do {
                            puVar2 = (undefined4 *)(puVar27 + lVar33);
                            uVar3 = puVar2[1];
                            uVar4 = puVar2[2];
                            uVar5 = puVar2[3];
                            uVar28 = *(undefined8 *)(puVar27 + lVar33 + 0x10);
                            uVar6 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x10) + 8);
                            uVar7 = *(undefined8 *)(puVar27 + lVar33 + 0x20);
                            uVar8 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x20) + 8);
                            uVar9 = *(undefined8 *)(puVar27 + lVar33 + 0x30);
                            uVar10 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x30) + 8);
                            puVar1 = (undefined4 *)(puVar30 + lVar33);
                            *puVar1 = *puVar2;
                            puVar1[1] = uVar3;
                            puVar1[2] = uVar4;
                            puVar1[3] = uVar5;
                            *(undefined8 *)(puVar30 + lVar33 + 0x10) = uVar28;
                            *(undefined8 *)((long)(puVar30 + lVar33 + 0x10) + 8) = uVar6;
                            *(undefined8 *)(puVar30 + lVar33 + 0x20) = uVar7;
                            *(undefined8 *)((long)(puVar30 + lVar33 + 0x20) + 8) = uVar8;
                            *(undefined8 *)(puVar30 + lVar33 + 0x30) = uVar9;
                            *(undefined8 *)((long)(puVar30 + lVar33 + 0x30) + 8) = uVar10;
                            lVar33 = lVar33 + 0x40;
                            lVar34 = lVar34 + 2;
                          } while (lVar34 != 0);
                        }
                        puVar27 = PTR_0010cef0;
                        if (uVar31 != 0) {
                          puVar1 = (undefined4 *)(PTR_0010ce50 + lVar33);
                          uVar3 = puVar1[1];
                          uVar4 = puVar1[2];
                          uVar5 = puVar1[3];
                          uVar28 = *(undefined8 *)(PTR_0010ce50 + lVar33 + 0x10);
                          uVar6 = *(undefined8 *)((long)(PTR_0010ce50 + lVar33 + 0x10) + 8);
                          puVar2 = (undefined4 *)(PTR_0010cef0 + lVar33);
                          *puVar2 = *puVar1;
                          puVar2[1] = uVar3;
                          puVar2[2] = uVar4;
                          puVar2[3] = uVar5;
                          *(undefined8 *)(puVar27 + lVar33 + 0x10) = uVar28;
                          *(undefined8 *)((long)(puVar27 + lVar33 + 0x10) + 8) = uVar6;
                        }
                        if (uVar26 == uVar35) goto LAB_001085e0;
                        puVar27 = PTR_0010ce50 + uVar35;
                        puVar30 = PTR_0010cef0 + uVar35;
                      }
                      lVar34 = 0;
                      do {
                        puVar30[lVar34] = puVar27[lVar34];
                        lVar34 = lVar34 + 1;
                      } while ((byte)((char)uVar25 + (char)lVar34) < bVar36);
                    }
LAB_001085e0:
                    *PTR_0010cee8 = bVar36;
                  }
                  puVar30 = PTR_0010cf28;
                  puVar27 = PTR_0010ce50;
                  x2com_build_msg(PTR_0010cf28,0,PTR_0010ce50);
                  cVar23 = x2com_get_msg_last_pos(puVar30);
                  x2com_tx_msg(param_1,param_2,puVar30,cVar23 + '\x01');
                  x2com_start_ack_timer(param_1,param_2);
                  puVar30 = PTR_0010cea8;
                  bVar37 = *puVar32;
                  if (bVar37 == 0) {
                    *PTR_0010ceb0 = 1;
                    *puVar11 = 1;
                    *puVar30 = 1;
                    uVar28 = 0x10;
                  }
                  else {
                    *puVar11 = 1;
                    *puVar30 = 1;
                    bVar36 = *PTR_0010cee8;
                    uVar28 = 0x11;
                    if ((ulong)bVar36 != 0) {
                      bVar24 = 0xe;
                      if (bVar37 < 0xe) {
                        bVar24 = bVar37;
                      }
                      uVar26 = 0;
                      bVar29 = 0;
                      do {
                        cVar23 = PTR_0010cef0[uVar26];
                        uVar31 = 1;
                        do {
                          lVar34 = uVar31 - 1;
                          if (bVar24 <= uVar31) break;
                          uVar31 = uVar31 + 1;
                        } while (cVar23 != puVar27[lVar34]);
                        if (cVar23 != puVar27[lVar34]) {
                          uVar31 = (ulong)bVar29;
                          bVar29 = bVar29 + 1;
                          acStack_46[uVar31] = cVar23;
                        }
                        uVar26 = uVar26 + 1;
                      } while (uVar26 != bVar36);
                      if (bVar29 != 0) goto LAB_001086ce;
                    }
                  }
                  goto LAB_001086eb;
                }
                if ((*PTR_0010ce88 == '\0' & *PTR_0010ce68) == 0) {
                  if (*PTR_0010ce60 == '\0') {
                    uVar28 = 0;
                    goto LAB_00107eb1;
                  }
                  *PTR_0010ce60 = 0;
                  *PTR_0010ce98 = 0;
                  *PTR_0010ce80 = 0;
                  *PTR_0010ce90 = 0;
                  puVar30 = PTR_0010cf10;
                  puVar32 = PTR_0010ce78;
                  puVar27 = PTR_0010ce70;
                  bVar37 = *PTR_0010ce78;
                  if (bVar37 != 0) {
                    bVar36 = 0xe;
                    if (bVar37 < 0xe) {
                      bVar36 = bVar37;
                    }
                    if (bVar36 != 0) {
                      uVar26 = (ulong)(byte)(bVar36 - 1) + 1;
                      if (uVar26 < 0x20) {
                        uVar25 = 0;
                      }
                      else {
                        uVar25 = (uint)uVar26 & 0xffffffe0;
                        uVar31 = (ulong)uVar25;
                        lVar34 = (uVar31 - 0x20 >> 5) + 1;
                        uVar35 = (ulong)((uint)lVar34 & 1);
                        if (uVar31 - 0x20 == 0) {
                          lVar33 = 0;
                        }
                        else {
                          lVar34 = uVar35 - lVar34;
                          lVar33 = 0;
                          do {
                            puVar2 = (undefined4 *)(puVar27 + lVar33);
                            uVar3 = puVar2[1];
                            uVar4 = puVar2[2];
                            uVar5 = puVar2[3];
                            uVar28 = *(undefined8 *)(puVar27 + lVar33 + 0x10);
                            uVar6 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x10) + 8);
                            uVar7 = *(undefined8 *)(puVar27 + lVar33 + 0x20);
                            uVar8 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x20) + 8);
                            uVar9 = *(undefined8 *)(puVar27 + lVar33 + 0x30);
                            uVar10 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x30) + 8);
                            puVar1 = (undefined4 *)(puVar30 + lVar33);
                            *puVar1 = *puVar2;
                            puVar1[1] = uVar3;
                            puVar1[2] = uVar4;
                            puVar1[3] = uVar5;
                            *(undefined8 *)(puVar30 + lVar33 + 0x10) = uVar28;
                            *(undefined8 *)((long)(puVar30 + lVar33 + 0x10) + 8) = uVar6;
                            *(undefined8 *)(puVar30 + lVar33 + 0x20) = uVar7;
                            *(undefined8 *)((long)(puVar30 + lVar33 + 0x20) + 8) = uVar8;
                            *(undefined8 *)(puVar30 + lVar33 + 0x30) = uVar9;
                            *(undefined8 *)((long)(puVar30 + lVar33 + 0x30) + 8) = uVar10;
                            lVar33 = lVar33 + 0x40;
                            lVar34 = lVar34 + 2;
                          } while (lVar34 != 0);
                        }
                        puVar27 = PTR_0010cf10;
                        if (uVar35 != 0) {
                          puVar1 = (undefined4 *)(PTR_0010ce70 + lVar33);
                          uVar3 = puVar1[1];
                          uVar4 = puVar1[2];
                          uVar5 = puVar1[3];
                          uVar28 = *(undefined8 *)(PTR_0010ce70 + lVar33 + 0x10);
                          uVar6 = *(undefined8 *)((long)(PTR_0010ce70 + lVar33 + 0x10) + 8);
                          puVar2 = (undefined4 *)(PTR_0010cf10 + lVar33);
                          *puVar2 = *puVar1;
                          puVar2[1] = uVar3;
                          puVar2[2] = uVar4;
                          puVar2[3] = uVar5;
                          *(undefined8 *)(puVar27 + lVar33 + 0x10) = uVar28;
                          *(undefined8 *)((long)(puVar27 + lVar33 + 0x10) + 8) = uVar6;
                        }
                        if (uVar26 == uVar31) goto LAB_00108936;
                        puVar27 = PTR_0010ce70 + uVar31;
                        puVar30 = PTR_0010cf10 + uVar31;
                      }
                      lVar34 = 0;
                      do {
                        puVar30[lVar34] = puVar27[lVar34];
                        lVar34 = lVar34 + 1;
                      } while ((byte)((char)uVar25 + (char)lVar34) < bVar36);
                    }
LAB_00108936:
                    *PTR_0010cf08 = bVar36;
                  }
                  puVar30 = PTR_0010cf28;
                  puVar27 = PTR_0010ce70;
                  x2com_build_msg(PTR_0010cf28,4,PTR_0010ce70,puVar32);
                  cVar23 = x2com_get_msg_last_pos(puVar30);
                  x2com_tx_msg(param_1,param_2,puVar30,cVar23 + '\x01');
                  x2com_start_resp_timer(param_1,param_2);
                  bVar37 = *puVar32;
                  if (bVar37 == 0) {
                    *PTR_0010ce90 = 1;
                    *puVar12 = 1;
                    *PTR_0010ce88 = 1;
                    uVar28 = 0x12;
                  }
                  else {
                    *puVar12 = 1;
                    *PTR_0010ce88 = 1;
                    bVar36 = *PTR_0010cf08;
                    uVar28 = 0x13;
                    if ((ulong)bVar36 != 0) {
                      bVar24 = 0xe;
                      if (bVar37 < 0xe) {
                        bVar24 = bVar37;
                      }
                      uVar26 = 0;
                      bVar29 = 0;
                      do {
                        cVar23 = PTR_0010cf10[uVar26];
                        uVar31 = 1;
                        do {
                          lVar34 = uVar31 - 1;
                          if (bVar24 <= uVar31) break;
                          uVar31 = uVar31 + 1;
                        } while (cVar23 != puVar27[lVar34]);
                        if (cVar23 != puVar27[lVar34]) {
                          uVar31 = (ulong)bVar29;
                          bVar29 = bVar29 + 1;
                          acStack_46[uVar31] = cVar23;
                        }
                        uVar26 = uVar26 + 1;
                      } while (uVar26 != bVar36);
                      if (bVar29 != 0) goto LAB_00108a29;
                    }
                  }
LAB_00108a4d:
                  bVar29 = 0;
                }
                else {
                  bVar37 = *PTR_0010ce78;
                  if (bVar37 != 0) {
                    bVar36 = 0xe;
                    if (bVar37 < 0xe) {
                      bVar36 = bVar37;
                    }
                    if (bVar36 != 0) {
                      uVar26 = (ulong)(byte)(bVar36 - 1) + 1;
                      if (uVar26 < 0x20) {
                        uVar25 = 0;
                        puVar27 = PTR_0010ce70;
                        puVar32 = PTR_0010cf10;
                      }
                      else {
                        uVar25 = (uint)uVar26 & 0xffffffe0;
                        uVar31 = (ulong)uVar25;
                        lVar34 = (uVar31 - 0x20 >> 5) + 1;
                        uVar35 = (ulong)((uint)lVar34 & 1);
                        if (uVar31 - 0x20 == 0) {
                          lVar33 = 0;
                        }
                        else {
                          lVar34 = uVar35 - lVar34;
                          lVar33 = 0;
                          do {
                            puVar2 = (undefined4 *)(puVar13 + lVar33);
                            uVar3 = puVar2[1];
                            uVar4 = puVar2[2];
                            uVar5 = puVar2[3];
                            uVar28 = *(undefined8 *)(puVar13 + lVar33 + 0x10);
                            uVar6 = *(undefined8 *)((long)(puVar13 + lVar33 + 0x10) + 8);
                            uVar7 = *(undefined8 *)(puVar13 + lVar33 + 0x20);
                            uVar8 = *(undefined8 *)((long)(puVar13 + lVar33 + 0x20) + 8);
                            uVar9 = *(undefined8 *)(puVar13 + lVar33 + 0x30);
                            uVar10 = *(undefined8 *)((long)(puVar13 + lVar33 + 0x30) + 8);
                            puVar1 = (undefined4 *)(puVar19 + lVar33);
                            *puVar1 = *puVar2;
                            puVar1[1] = uVar3;
                            puVar1[2] = uVar4;
                            puVar1[3] = uVar5;
                            *(undefined8 *)(puVar19 + lVar33 + 0x10) = uVar28;
                            *(undefined8 *)((long)(puVar19 + lVar33 + 0x10) + 8) = uVar6;
                            *(undefined8 *)(puVar19 + lVar33 + 0x20) = uVar7;
                            *(undefined8 *)((long)(puVar19 + lVar33 + 0x20) + 8) = uVar8;
                            *(undefined8 *)(puVar19 + lVar33 + 0x30) = uVar9;
                            *(undefined8 *)((long)(puVar19 + lVar33 + 0x30) + 8) = uVar10;
                            lVar33 = lVar33 + 0x40;
                            lVar34 = lVar34 + 2;
                          } while (lVar34 != 0);
                        }
                        puVar27 = PTR_0010cf10;
                        if (uVar35 != 0) {
                          puVar1 = (undefined4 *)(PTR_0010ce70 + lVar33);
                          uVar3 = puVar1[1];
                          uVar4 = puVar1[2];
                          uVar5 = puVar1[3];
                          uVar28 = *(undefined8 *)(PTR_0010ce70 + lVar33 + 0x10);
                          uVar6 = *(undefined8 *)((long)(PTR_0010ce70 + lVar33 + 0x10) + 8);
                          puVar2 = (undefined4 *)(PTR_0010cf10 + lVar33);
                          *puVar2 = *puVar1;
                          puVar2[1] = uVar3;
                          puVar2[2] = uVar4;
                          puVar2[3] = uVar5;
                          *(undefined8 *)(puVar27 + lVar33 + 0x10) = uVar28;
                          *(undefined8 *)((long)(puVar27 + lVar33 + 0x10) + 8) = uVar6;
                        }
                        if (uVar26 == uVar31) goto LAB_001087cc;
                        puVar27 = PTR_0010ce70 + uVar31;
                        puVar32 = PTR_0010cf10 + uVar31;
                      }
                      lVar34 = 0;
                      do {
                        puVar32[lVar34] = puVar27[lVar34];
                        lVar34 = lVar34 + 1;
                      } while ((byte)((char)uVar25 + (char)lVar34) < bVar36);
                    }
LAB_001087cc:
                    *PTR_0010cf08 = bVar36;
                  }
                  puVar32 = PTR_0010cf28;
                  puVar27 = PTR_0010ce70;
                  x2com_build_msg(PTR_0010cf28,4,PTR_0010ce70,puVar14);
                  cVar23 = x2com_get_msg_last_pos(puVar32);
                  x2com_tx_msg(param_1,param_2,puVar32,cVar23 + '\x01');
                  x2com_start_resp_timer(param_1,param_2);
                  bVar37 = *puVar14;
                  if ((bVar37 == 0) || (uVar28 = 0x13, bVar37 == DAT_0010d014)) {
                    *PTR_0010ce90 = 1;
                    uVar28 = 0x12;
                  }
                  *PTR_0010ce88 = 1;
                  if ((bVar37 == 0) || (bVar36 = *PTR_0010cf08, (ulong)bVar36 == 0))
                  goto LAB_00108a4d;
                  bVar24 = 0xe;
                  if (bVar37 < 0xe) {
                    bVar24 = bVar37;
                  }
                  uVar26 = 0;
                  bVar29 = 0;
                  do {
                    cVar23 = PTR_0010cf10[uVar26];
                    uVar31 = 1;
                    do {
                      lVar34 = uVar31 - 1;
                      if (bVar24 <= uVar31) break;
                      uVar31 = uVar31 + 1;
                    } while (cVar23 != puVar27[lVar34]);
                    if (cVar23 != puVar27[lVar34]) {
                      uVar31 = (ulong)bVar29;
                      bVar29 = bVar29 + 1;
                      acStack_46[uVar31] = cVar23;
                    }
                    uVar26 = uVar26 + 1;
                  } while (uVar26 != bVar36);
                  if (bVar29 == 0) goto LAB_00108a4d;
LAB_00108a29:
                  memcpy(PTR_0010cf10,acStack_46,(ulong)bVar29);
                }
                *PTR_0010cf08 = bVar29;
                DAT_0010d014 = bVar37;
                goto LAB_00107eb1;
              }
              __android_log_print(6,"BluetoothChatService","x2com_xmit - cwa progress");
              puVar30 = PTR_0010cef0;
              puVar32 = PTR_0010ce58;
              puVar27 = PTR_0010ce50;
              bVar37 = *PTR_0010ce58;
              if (bVar37 != 0) {
                bVar36 = 0xe;
                if (bVar37 < 0xe) {
                  bVar36 = bVar37;
                }
                if (bVar36 != 0) {
                  uVar26 = (ulong)(byte)(bVar36 - 1) + 1;
                  if (uVar26 < 0x20) {
                    uVar25 = 0;
                  }
                  else {
                    uVar25 = (uint)uVar26 & 0xffffffe0;
                    uVar31 = (ulong)uVar25;
                    lVar34 = (uVar31 - 0x20 >> 5) + 1;
                    uVar35 = (ulong)((uint)lVar34 & 1);
                    if (uVar31 - 0x20 == 0) {
                      lVar33 = 0;
                    }
                    else {
                      lVar34 = uVar35 - lVar34;
                      lVar33 = 0;
                      do {
                        puVar2 = (undefined4 *)(puVar27 + lVar33);
                        uVar3 = puVar2[1];
                        uVar4 = puVar2[2];
                        uVar5 = puVar2[3];
                        uVar28 = *(undefined8 *)(puVar27 + lVar33 + 0x10);
                        uVar6 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x10) + 8);
                        uVar7 = *(undefined8 *)(puVar27 + lVar33 + 0x20);
                        uVar8 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x20) + 8);
                        uVar9 = *(undefined8 *)(puVar27 + lVar33 + 0x30);
                        uVar10 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x30) + 8);
                        puVar1 = (undefined4 *)(puVar30 + lVar33);
                        *puVar1 = *puVar2;
                        puVar1[1] = uVar3;
                        puVar1[2] = uVar4;
                        puVar1[3] = uVar5;
                        *(undefined8 *)(puVar30 + lVar33 + 0x10) = uVar28;
                        *(undefined8 *)((long)(puVar30 + lVar33 + 0x10) + 8) = uVar6;
                        *(undefined8 *)(puVar30 + lVar33 + 0x20) = uVar7;
                        *(undefined8 *)((long)(puVar30 + lVar33 + 0x20) + 8) = uVar8;
                        *(undefined8 *)(puVar30 + lVar33 + 0x30) = uVar9;
                        *(undefined8 *)((long)(puVar30 + lVar33 + 0x30) + 8) = uVar10;
                        lVar33 = lVar33 + 0x40;
                        lVar34 = lVar34 + 2;
                      } while (lVar34 != 0);
                    }
                    puVar27 = PTR_0010cef0;
                    if (uVar35 != 0) {
                      puVar1 = (undefined4 *)(PTR_0010ce50 + lVar33);
                      uVar3 = puVar1[1];
                      uVar4 = puVar1[2];
                      uVar5 = puVar1[3];
                      uVar28 = *(undefined8 *)(PTR_0010ce50 + lVar33 + 0x10);
                      uVar6 = *(undefined8 *)((long)(PTR_0010ce50 + lVar33 + 0x10) + 8);
                      puVar2 = (undefined4 *)(PTR_0010cef0 + lVar33);
                      *puVar2 = *puVar1;
                      puVar2[1] = uVar3;
                      puVar2[2] = uVar4;
                      puVar2[3] = uVar5;
                      *(undefined8 *)(puVar27 + lVar33 + 0x10) = uVar28;
                      *(undefined8 *)((long)(puVar27 + lVar33 + 0x10) + 8) = uVar6;
                    }
                    if (uVar26 == uVar31) goto LAB_001083fe;
                    puVar27 = PTR_0010ce50 + uVar31;
                    puVar30 = PTR_0010cef0 + uVar31;
                  }
                  lVar34 = 0;
                  do {
                    puVar30[lVar34] = puVar27[lVar34];
                    lVar34 = lVar34 + 1;
                  } while ((byte)((char)uVar25 + (char)lVar34) < bVar36);
                }
LAB_001083fe:
                *PTR_0010cee8 = bVar36;
              }
              puVar30 = PTR_0010cf28;
              puVar27 = PTR_0010ce50;
              x2com_build_msg(PTR_0010cf28,0,PTR_0010ce50,puVar32);
              cVar23 = x2com_get_msg_last_pos(puVar30);
              x2com_tx_msg(param_1,param_2,puVar30,cVar23 + '\x01');
              x2com_start_ack_timer(param_1,param_2);
              bVar37 = *puVar32;
              if ((bVar37 == 0) || (uVar28 = 0x11, bVar37 == DAT_0010d013)) {
                *PTR_0010ceb0 = 1;
                uVar28 = 0x10;
              }
              *puVar15 = 1;
              if ((bVar37 == 0) || (bVar36 = *PTR_0010cee8, (ulong)bVar36 == 0)) {
LAB_001086eb:
                bVar29 = 0;
              }
              else {
                bVar24 = 0xe;
                if (bVar37 < 0xe) {
                  bVar24 = bVar37;
                }
                uVar26 = 0;
                bVar29 = 0;
                do {
                  cVar23 = PTR_0010cef0[uVar26];
                  uVar31 = 1;
                  do {
                    lVar34 = uVar31 - 1;
                    if (bVar24 <= uVar31) break;
                    uVar31 = uVar31 + 1;
                  } while (cVar23 != puVar27[lVar34]);
                  if (cVar23 != puVar27[lVar34]) {
                    uVar31 = (ulong)bVar29;
                    bVar29 = bVar29 + 1;
                    acStack_46[uVar31] = cVar23;
                  }
                  uVar26 = uVar26 + 1;
                } while (uVar26 != bVar36);
                if (bVar29 == 0) goto LAB_001086eb;
LAB_001086ce:
                memcpy(PTR_0010cef0,acStack_46,(ulong)bVar29);
              }
              *PTR_0010cee8 = bVar29;
              DAT_0010d013 = bVar37;
              goto LAB_00107eb1;
            }
            *PTR_0010ced8 = 0;
            pcVar22 = DAT_0010cf38;
            puVar27 = PTR_0010cf28;
            x2com_build_msg(PTR_0010cf28,3,PTR_0010cf30,DAT_0010cf38);
            cVar23 = x2com_get_msg_last_pos(puVar27);
            x2com_tx_msg(param_1,param_2,puVar27,cVar23 + '\x01');
            cVar23 = *pcVar22;
            if (cVar23 == '\0') {
              uVar28 = 0xe;
              goto LAB_00107eb1;
            }
            *puVar18 = 1;
          }
          else {
            x2com_build_msg(PTR_0010cf28,3,PTR_0010cf30,DAT_0010cf38);
            cVar23 = x2com_get_msg_last_pos(puVar21);
            x2com_tx_msg(param_1,param_2,puVar21,cVar23 + '\x01');
            cVar23 = *pcVar22;
            if ((cVar23 == '\0') || (cVar23 == DAT_0010d012)) {
              *puVar18 = 0;
              uVar28 = 0xe;
              goto LAB_00107eb1;
            }
          }
          uVar28 = 0xf;
          DAT_0010d012 = cVar23;
          goto LAB_00107eb1;
        }
        *PTR_0010ce20 = 0;
        puVar30 = PTR_0010cf28;
        puVar32 = PTR_0010ce38;
        x2com_build_msg(PTR_0010cf28,1,PTR_0010ce30,PTR_0010ce38);
        cVar23 = x2com_get_msg_last_pos(puVar30);
        x2com_tx_msg(param_1,param_2,puVar30,cVar23 + '\x01');
        cVar23 = *puVar32;
        if (cVar23 == '\0') {
          uVar28 = 0xc;
          goto LAB_00107eb1;
        }
        *puVar27 = 1;
      }
      else {
        x2com_build_msg(PTR_0010cf28,1,PTR_0010ce30,PTR_0010ce38);
        cVar23 = x2com_get_msg_last_pos(puVar21);
        x2com_tx_msg(param_1,param_2,puVar21,cVar23 + '\x01');
        cVar23 = *puVar32;
        if ((cVar23 == '\0') || (cVar23 == DAT_0010d011)) {
          *puVar27 = 0;
          uVar28 = 0xc;
          goto LAB_00107eb1;
        }
      }
      uVar28 = 0xd;
      DAT_0010d011 = cVar23;
      goto LAB_00107eb1;
    }
    *PTR_0010cec0 = 0;
    puVar32 = PTR_0010cf28;
    puVar27 = PTR_0010cf20;
    x2com_build_msg(PTR_0010cf28,5,PTR_0010cf18,PTR_0010cf20);
    cVar23 = x2com_get_msg_last_pos(puVar32);
    x2com_tx_msg(param_1,param_2,puVar32,cVar23 + '\x01');
    cVar23 = *puVar27;
    if (cVar23 == '\0') {
      uVar28 = 10;
      goto LAB_00107eb1;
    }
    *puVar16 = 1;
  }
  else {
    x2com_build_msg(PTR_0010cf28,5,PTR_0010cf18,PTR_0010cf20);
    cVar23 = x2com_get_msg_last_pos(puVar21);
    x2com_tx_msg(param_1,param_2,puVar21,cVar23 + '\x01');
    cVar23 = *puVar20;
    if ((cVar23 == '\0') || (cVar23 == DAT_0010d010)) {
      *puVar16 = 0;
      uVar28 = 10;
      goto LAB_00107eb1;
    }
  }
  uVar28 = 0xb;
  DAT_0010d010 = cVar23;
LAB_00107eb1:
  if (*(long *)(in_FS_OFFSET + 0x28) != lStack_38) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return uVar28;
}



// === x2com_is_tx_ready at 00105710 (6 bytes) ===

/* WARNING: Switch with 1 destination removed at 0x00105710 */

undefined4 x2com_is_tx_ready(long *param_1,undefined8 param_2)

{
  undefined4 uVar1;
  long lVar2;
  long lVar3;
  
  lVar2 = (**(code **)(*param_1 + 0x30))
                    (param_1,"com/quadzillapower/iQuad/bluetooth/BluetoothChatService");
  if ((lVar2 != 0) &&
     (lVar3 = (**(code **)(*param_1 + 0x108))(param_1,lVar2,"getWriteStatus",&DAT_00109449),
     lVar3 != 0)) {
    uVar1 = (**(code **)(*param_1 + 0x188))(param_1,param_2,lVar3);
    (**(code **)(*param_1 + 0xb8))(param_1,lVar2);
    return uVar1;
  }
  return 0;
}



// === x2com_build_msg at 00105720 (6 bytes) ===

/* WARNING: Switch with 1 destination removed at 0x00105720 */

int x2com_build_msg(byte *param_1,undefined8 param_2,undefined8 param_3,char *param_4)

{
  char cVar1;
  byte bVar2;
  byte bVar3;
  
  *param_1 = (char)param_2 << 4 | *param_1 & 0xf;
  cVar1 = x2com_set_msg_data(param_1 + 1,param_2,param_3,param_4);
  bVar2 = cVar1 + 1;
  *param_1 = *param_1 & 0xf0 | bVar2 & 0xf;
  bVar3 = x2com_generate_crc(param_1,(ulong)bVar2);
  param_1[bVar2] = bVar3;
  return 2 - (uint)(*param_4 == '\0');
}



// === x2com_tx_msg at 00105730 (6 bytes) ===

/* WARNING: Switch with 1 destination removed at 0x00105730 */

void x2com_tx_msg(long *param_1,undefined8 param_2,undefined8 param_3,undefined1 param_4)

{
  long lVar1;
  long lVar2;
  long lVar3;
  
  lVar1 = (**(code **)(*param_1 + 0x30))
                    (param_1,"com/quadzillapower/iQuad/bluetooth/BluetoothChatService");
  if ((lVar1 != 0) &&
     (lVar2 = (**(code **)(*param_1 + 0x108))(param_1,lVar1,"writeAV","([B)V"), lVar2 != 0)) {
    lVar3 = (**(code **)(*param_1 + 0x580))(param_1,param_4);
    if (lVar3 != 0) {
      (**(code **)(*param_1 + 0x680))(param_1,lVar3,0,param_4,param_3);
      (**(code **)(*param_1 + 0x1e8))(param_1,param_2,lVar2,lVar3);
      (**(code **)(*param_1 + 0xb8))(param_1,lVar3);
    }
                    /* WARNING: Could not recover jumptable at 0x00105895. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (**(code **)(*param_1 + 0xb8))(param_1,lVar1);
    return;
  }
  return;
}



// === x2com_start_ack_timer at 00105740 (6 bytes) ===

/* WARNING: Switch with 1 destination removed at 0x00105740 */

void x2com_start_ack_timer(long *param_1,undefined8 param_2)

{
  long lVar1;
  long lVar2;
  
  lVar1 = (**(code **)(*param_1 + 0x30))
                    (param_1,"com/quadzillapower/iQuad/bluetooth/BluetoothChatService");
  if ((lVar1 != 0) &&
     (lVar2 = (**(code **)(*param_1 + 0x108))(param_1,lVar1,"btsStartAckTimer",&DAT_00109478),
     lVar2 != 0)) {
    (**(code **)(*param_1 + 0x1e8))(param_1,param_2,lVar2);
                    /* WARNING: Could not recover jumptable at 0x00105d4b. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (**(code **)(*param_1 + 0xb8))(param_1,lVar1);
    return;
  }
  return;
}



// === x2com_start_resp_timer at 00105750 (6 bytes) ===

/* WARNING: Switch with 1 destination removed at 0x00105750 */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void x2com_start_resp_timer(long *param_1,undefined8 param_2)

{
  long lVar1;
  long lVar2;
  
  lVar1 = (**(code **)(*param_1 + 0x30))
                    (param_1,"com/quadzillapower/iQuad/bluetooth/BluetoothChatService");
  if ((lVar1 != 0) &&
     (lVar2 = (**(code **)(*param_1 + 0x108))(param_1,lVar1,"btsStartRespTimer",&DAT_00109478),
     lVar2 != 0)) {
    (**(code **)(*param_1 + 0x1e8))(param_1,param_2,lVar2);
                    /* WARNING: Could not recover jumptable at 0x00105ccb. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (**(code **)(*param_1 + 0xb8))(param_1,lVar1);
    return;
  }
  return;
}



// === x2com_get_msg_last_pos at 00105f60 (5 bytes) ===

byte x2com_get_msg_last_pos(byte *param_1)

{
  return *param_1 & 0xf;
}



// === Java_com_quadzillapower_iQuad_bluetooth_BluetoothChatService_X2comHandleXmit at 00107d40 (5 bytes) ===

/* WARNING: Switch with 1 destination removed at 0x00105700 */

undefined8
Java_com_quadzillapower_iQuad_bluetooth_BluetoothChatService_X2comHandleXmit
          (undefined8 param_1,undefined8 param_2)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined8 uVar6;
  undefined8 uVar7;
  undefined8 uVar8;
  undefined8 uVar9;
  undefined8 uVar10;
  undefined *puVar11;
  undefined *puVar12;
  undefined *puVar13;
  undefined *puVar14;
  undefined *puVar15;
  undefined *puVar16;
  undefined *puVar17;
  undefined *puVar18;
  undefined *puVar19;
  undefined *puVar20;
  undefined *puVar21;
  char *pcVar22;
  char cVar23;
  byte bVar24;
  uint uVar25;
  ulong uVar26;
  undefined *puVar27;
  undefined8 uVar28;
  byte bVar29;
  undefined *puVar30;
  ulong uVar31;
  undefined *puVar32;
  long lVar33;
  long lVar34;
  ulong uVar35;
  byte bVar36;
  byte bVar37;
  long in_FS_OFFSET;
  char acStack_46 [14];
  long lStack_38;
  
  lStack_38 = *(long *)(in_FS_OFFSET + 0x28);
  cVar23 = x2com_is_tx_ready();
  pcVar22 = DAT_0010cf38;
  puVar21 = PTR_0010cf28;
  puVar20 = PTR_0010cf20;
  puVar19 = PTR_0010cf10;
  puVar18 = PTR_0010cee0;
  puVar17 = PTR_0010ced0;
  puVar16 = PTR_0010cec8;
  puVar15 = PTR_0010cea8;
  puVar14 = PTR_0010ce78;
  puVar13 = PTR_0010ce70;
  puVar12 = PTR_0010ce68;
  puVar11 = PTR_0010ce48;
  puVar30 = PTR_0010ce40;
  puVar32 = PTR_0010ce38;
  puVar27 = PTR_0010ce28;
  if (cVar23 == '\0') {
    uVar28 = 8;
    goto LAB_00107eb1;
  }
  if (*PTR_0010ced0 != '\0') {
    x2com_build_msg(PTR_0010cf28,2,PTR_0010cef8,PTR_0010cf00);
    cVar23 = x2com_get_msg_last_pos(puVar21);
    x2com_tx_msg(param_1,param_2,puVar21,cVar23 + '\x01');
    *puVar17 = 0;
    uVar28 = 9;
    goto LAB_00107eb1;
  }
  if (*PTR_0010cec8 == '\0') {
    if (*PTR_0010cec0 == '\0') {
      if (*PTR_0010ce28 == '\0') {
        if (*PTR_0010ce20 == '\0') {
          if (*PTR_0010cee0 == '\0') {
            if (*PTR_0010ced8 == '\0') {
              if ((*PTR_0010cea8 == '\0' & *PTR_0010ce48) == 0) {
                if (*PTR_0010ce40 != '\0') {
                  __android_log_print(6,"BluetoothChatService","x2com_xmit - cwa needed");
                  *puVar30 = 0;
                  *PTR_0010ceb8 = 0;
                  *PTR_0010cea0 = 0;
                  *PTR_0010ceb0 = 0;
                  puVar30 = PTR_0010cef0;
                  puVar32 = PTR_0010ce58;
                  puVar27 = PTR_0010ce50;
                  bVar37 = *PTR_0010ce58;
                  if (bVar37 != 0) {
                    bVar36 = 0xe;
                    if (bVar37 < 0xe) {
                      bVar36 = bVar37;
                    }
                    if (bVar36 != 0) {
                      uVar26 = (ulong)(byte)(bVar36 - 1) + 1;
                      if (uVar26 < 0x20) {
                        uVar25 = 0;
                      }
                      else {
                        uVar25 = (uint)uVar26 & 0xffffffe0;
                        uVar35 = (ulong)uVar25;
                        lVar34 = (uVar35 - 0x20 >> 5) + 1;
                        uVar31 = (ulong)((uint)lVar34 & 1);
                        if (uVar35 - 0x20 == 0) {
                          lVar33 = 0;
                        }
                        else {
                          lVar34 = uVar31 - lVar34;
                          lVar33 = 0;
                          do {
                            puVar2 = (undefined4 *)(puVar27 + lVar33);
                            uVar3 = puVar2[1];
                            uVar4 = puVar2[2];
                            uVar5 = puVar2[3];
                            uVar28 = *(undefined8 *)(puVar27 + lVar33 + 0x10);
                            uVar6 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x10) + 8);
                            uVar7 = *(undefined8 *)(puVar27 + lVar33 + 0x20);
                            uVar8 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x20) + 8);
                            uVar9 = *(undefined8 *)(puVar27 + lVar33 + 0x30);
                            uVar10 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x30) + 8);
                            puVar1 = (undefined4 *)(puVar30 + lVar33);
                            *puVar1 = *puVar2;
                            puVar1[1] = uVar3;
                            puVar1[2] = uVar4;
                            puVar1[3] = uVar5;
                            *(undefined8 *)(puVar30 + lVar33 + 0x10) = uVar28;
                            *(undefined8 *)((long)(puVar30 + lVar33 + 0x10) + 8) = uVar6;
                            *(undefined8 *)(puVar30 + lVar33 + 0x20) = uVar7;
                            *(undefined8 *)((long)(puVar30 + lVar33 + 0x20) + 8) = uVar8;
                            *(undefined8 *)(puVar30 + lVar33 + 0x30) = uVar9;
                            *(undefined8 *)((long)(puVar30 + lVar33 + 0x30) + 8) = uVar10;
                            lVar33 = lVar33 + 0x40;
                            lVar34 = lVar34 + 2;
                          } while (lVar34 != 0);
                        }
                        puVar27 = PTR_0010cef0;
                        if (uVar31 != 0) {
                          puVar1 = (undefined4 *)(PTR_0010ce50 + lVar33);
                          uVar3 = puVar1[1];
                          uVar4 = puVar1[2];
                          uVar5 = puVar1[3];
                          uVar28 = *(undefined8 *)(PTR_0010ce50 + lVar33 + 0x10);
                          uVar6 = *(undefined8 *)((long)(PTR_0010ce50 + lVar33 + 0x10) + 8);
                          puVar2 = (undefined4 *)(PTR_0010cef0 + lVar33);
                          *puVar2 = *puVar1;
                          puVar2[1] = uVar3;
                          puVar2[2] = uVar4;
                          puVar2[3] = uVar5;
                          *(undefined8 *)(puVar27 + lVar33 + 0x10) = uVar28;
                          *(undefined8 *)((long)(puVar27 + lVar33 + 0x10) + 8) = uVar6;
                        }
                        if (uVar26 == uVar35) goto LAB_001085e0;
                        puVar27 = PTR_0010ce50 + uVar35;
                        puVar30 = PTR_0010cef0 + uVar35;
                      }
                      lVar34 = 0;
                      do {
                        puVar30[lVar34] = puVar27[lVar34];
                        lVar34 = lVar34 + 1;
                      } while ((byte)((char)uVar25 + (char)lVar34) < bVar36);
                    }
LAB_001085e0:
                    *PTR_0010cee8 = bVar36;
                  }
                  puVar30 = PTR_0010cf28;
                  puVar27 = PTR_0010ce50;
                  x2com_build_msg(PTR_0010cf28,0,PTR_0010ce50);
                  cVar23 = x2com_get_msg_last_pos(puVar30);
                  x2com_tx_msg(param_1,param_2,puVar30,cVar23 + '\x01');
                  x2com_start_ack_timer(param_1,param_2);
                  puVar30 = PTR_0010cea8;
                  bVar37 = *puVar32;
                  if (bVar37 == 0) {
                    *PTR_0010ceb0 = 1;
                    *puVar11 = 1;
                    *puVar30 = 1;
                    uVar28 = 0x10;
                  }
                  else {
                    *puVar11 = 1;
                    *puVar30 = 1;
                    bVar36 = *PTR_0010cee8;
                    uVar28 = 0x11;
                    if ((ulong)bVar36 != 0) {
                      bVar24 = 0xe;
                      if (bVar37 < 0xe) {
                        bVar24 = bVar37;
                      }
                      uVar26 = 0;
                      bVar29 = 0;
                      do {
                        cVar23 = PTR_0010cef0[uVar26];
                        uVar31 = 1;
                        do {
                          lVar34 = uVar31 - 1;
                          if (bVar24 <= uVar31) break;
                          uVar31 = uVar31 + 1;
                        } while (cVar23 != puVar27[lVar34]);
                        if (cVar23 != puVar27[lVar34]) {
                          uVar31 = (ulong)bVar29;
                          bVar29 = bVar29 + 1;
                          acStack_46[uVar31] = cVar23;
                        }
                        uVar26 = uVar26 + 1;
                      } while (uVar26 != bVar36);
                      if (bVar29 != 0) goto LAB_001086ce;
                    }
                  }
                  goto LAB_001086eb;
                }
                if ((*PTR_0010ce88 == '\0' & *PTR_0010ce68) == 0) {
                  if (*PTR_0010ce60 == '\0') {
                    uVar28 = 0;
                    goto LAB_00107eb1;
                  }
                  *PTR_0010ce60 = 0;
                  *PTR_0010ce98 = 0;
                  *PTR_0010ce80 = 0;
                  *PTR_0010ce90 = 0;
                  puVar30 = PTR_0010cf10;
                  puVar32 = PTR_0010ce78;
                  puVar27 = PTR_0010ce70;
                  bVar37 = *PTR_0010ce78;
                  if (bVar37 != 0) {
                    bVar36 = 0xe;
                    if (bVar37 < 0xe) {
                      bVar36 = bVar37;
                    }
                    if (bVar36 != 0) {
                      uVar26 = (ulong)(byte)(bVar36 - 1) + 1;
                      if (uVar26 < 0x20) {
                        uVar25 = 0;
                      }
                      else {
                        uVar25 = (uint)uVar26 & 0xffffffe0;
                        uVar31 = (ulong)uVar25;
                        lVar34 = (uVar31 - 0x20 >> 5) + 1;
                        uVar35 = (ulong)((uint)lVar34 & 1);
                        if (uVar31 - 0x20 == 0) {
                          lVar33 = 0;
                        }
                        else {
                          lVar34 = uVar35 - lVar34;
                          lVar33 = 0;
                          do {
                            puVar2 = (undefined4 *)(puVar27 + lVar33);
                            uVar3 = puVar2[1];
                            uVar4 = puVar2[2];
                            uVar5 = puVar2[3];
                            uVar28 = *(undefined8 *)(puVar27 + lVar33 + 0x10);
                            uVar6 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x10) + 8);
                            uVar7 = *(undefined8 *)(puVar27 + lVar33 + 0x20);
                            uVar8 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x20) + 8);
                            uVar9 = *(undefined8 *)(puVar27 + lVar33 + 0x30);
                            uVar10 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x30) + 8);
                            puVar1 = (undefined4 *)(puVar30 + lVar33);
                            *puVar1 = *puVar2;
                            puVar1[1] = uVar3;
                            puVar1[2] = uVar4;
                            puVar1[3] = uVar5;
                            *(undefined8 *)(puVar30 + lVar33 + 0x10) = uVar28;
                            *(undefined8 *)((long)(puVar30 + lVar33 + 0x10) + 8) = uVar6;
                            *(undefined8 *)(puVar30 + lVar33 + 0x20) = uVar7;
                            *(undefined8 *)((long)(puVar30 + lVar33 + 0x20) + 8) = uVar8;
                            *(undefined8 *)(puVar30 + lVar33 + 0x30) = uVar9;
                            *(undefined8 *)((long)(puVar30 + lVar33 + 0x30) + 8) = uVar10;
                            lVar33 = lVar33 + 0x40;
                            lVar34 = lVar34 + 2;
                          } while (lVar34 != 0);
                        }
                        puVar27 = PTR_0010cf10;
                        if (uVar35 != 0) {
                          puVar1 = (undefined4 *)(PTR_0010ce70 + lVar33);
                          uVar3 = puVar1[1];
                          uVar4 = puVar1[2];
                          uVar5 = puVar1[3];
                          uVar28 = *(undefined8 *)(PTR_0010ce70 + lVar33 + 0x10);
                          uVar6 = *(undefined8 *)((long)(PTR_0010ce70 + lVar33 + 0x10) + 8);
                          puVar2 = (undefined4 *)(PTR_0010cf10 + lVar33);
                          *puVar2 = *puVar1;
                          puVar2[1] = uVar3;
                          puVar2[2] = uVar4;
                          puVar2[3] = uVar5;
                          *(undefined8 *)(puVar27 + lVar33 + 0x10) = uVar28;
                          *(undefined8 *)((long)(puVar27 + lVar33 + 0x10) + 8) = uVar6;
                        }
                        if (uVar26 == uVar31) goto LAB_00108936;
                        puVar27 = PTR_0010ce70 + uVar31;
                        puVar30 = PTR_0010cf10 + uVar31;
                      }
                      lVar34 = 0;
                      do {
                        puVar30[lVar34] = puVar27[lVar34];
                        lVar34 = lVar34 + 1;
                      } while ((byte)((char)uVar25 + (char)lVar34) < bVar36);
                    }
LAB_00108936:
                    *PTR_0010cf08 = bVar36;
                  }
                  puVar30 = PTR_0010cf28;
                  puVar27 = PTR_0010ce70;
                  x2com_build_msg(PTR_0010cf28,4,PTR_0010ce70,puVar32);
                  cVar23 = x2com_get_msg_last_pos(puVar30);
                  x2com_tx_msg(param_1,param_2,puVar30,cVar23 + '\x01');
                  x2com_start_resp_timer(param_1,param_2);
                  bVar37 = *puVar32;
                  if (bVar37 == 0) {
                    *PTR_0010ce90 = 1;
                    *puVar12 = 1;
                    *PTR_0010ce88 = 1;
                    uVar28 = 0x12;
                  }
                  else {
                    *puVar12 = 1;
                    *PTR_0010ce88 = 1;
                    bVar36 = *PTR_0010cf08;
                    uVar28 = 0x13;
                    if ((ulong)bVar36 != 0) {
                      bVar24 = 0xe;
                      if (bVar37 < 0xe) {
                        bVar24 = bVar37;
                      }
                      uVar26 = 0;
                      bVar29 = 0;
                      do {
                        cVar23 = PTR_0010cf10[uVar26];
                        uVar31 = 1;
                        do {
                          lVar34 = uVar31 - 1;
                          if (bVar24 <= uVar31) break;
                          uVar31 = uVar31 + 1;
                        } while (cVar23 != puVar27[lVar34]);
                        if (cVar23 != puVar27[lVar34]) {
                          uVar31 = (ulong)bVar29;
                          bVar29 = bVar29 + 1;
                          acStack_46[uVar31] = cVar23;
                        }
                        uVar26 = uVar26 + 1;
                      } while (uVar26 != bVar36);
                      if (bVar29 != 0) goto LAB_00108a29;
                    }
                  }
LAB_00108a4d:
                  bVar29 = 0;
                }
                else {
                  bVar37 = *PTR_0010ce78;
                  if (bVar37 != 0) {
                    bVar36 = 0xe;
                    if (bVar37 < 0xe) {
                      bVar36 = bVar37;
                    }
                    if (bVar36 != 0) {
                      uVar26 = (ulong)(byte)(bVar36 - 1) + 1;
                      if (uVar26 < 0x20) {
                        uVar25 = 0;
                        puVar27 = PTR_0010ce70;
                        puVar32 = PTR_0010cf10;
                      }
                      else {
                        uVar25 = (uint)uVar26 & 0xffffffe0;
                        uVar31 = (ulong)uVar25;
                        lVar34 = (uVar31 - 0x20 >> 5) + 1;
                        uVar35 = (ulong)((uint)lVar34 & 1);
                        if (uVar31 - 0x20 == 0) {
                          lVar33 = 0;
                        }
                        else {
                          lVar34 = uVar35 - lVar34;
                          lVar33 = 0;
                          do {
                            puVar2 = (undefined4 *)(puVar13 + lVar33);
                            uVar3 = puVar2[1];
                            uVar4 = puVar2[2];
                            uVar5 = puVar2[3];
                            uVar28 = *(undefined8 *)(puVar13 + lVar33 + 0x10);
                            uVar6 = *(undefined8 *)((long)(puVar13 + lVar33 + 0x10) + 8);
                            uVar7 = *(undefined8 *)(puVar13 + lVar33 + 0x20);
                            uVar8 = *(undefined8 *)((long)(puVar13 + lVar33 + 0x20) + 8);
                            uVar9 = *(undefined8 *)(puVar13 + lVar33 + 0x30);
                            uVar10 = *(undefined8 *)((long)(puVar13 + lVar33 + 0x30) + 8);
                            puVar1 = (undefined4 *)(puVar19 + lVar33);
                            *puVar1 = *puVar2;
                            puVar1[1] = uVar3;
                            puVar1[2] = uVar4;
                            puVar1[3] = uVar5;
                            *(undefined8 *)(puVar19 + lVar33 + 0x10) = uVar28;
                            *(undefined8 *)((long)(puVar19 + lVar33 + 0x10) + 8) = uVar6;
                            *(undefined8 *)(puVar19 + lVar33 + 0x20) = uVar7;
                            *(undefined8 *)((long)(puVar19 + lVar33 + 0x20) + 8) = uVar8;
                            *(undefined8 *)(puVar19 + lVar33 + 0x30) = uVar9;
                            *(undefined8 *)((long)(puVar19 + lVar33 + 0x30) + 8) = uVar10;
                            lVar33 = lVar33 + 0x40;
                            lVar34 = lVar34 + 2;
                          } while (lVar34 != 0);
                        }
                        puVar27 = PTR_0010cf10;
                        if (uVar35 != 0) {
                          puVar1 = (undefined4 *)(PTR_0010ce70 + lVar33);
                          uVar3 = puVar1[1];
                          uVar4 = puVar1[2];
                          uVar5 = puVar1[3];
                          uVar28 = *(undefined8 *)(PTR_0010ce70 + lVar33 + 0x10);
                          uVar6 = *(undefined8 *)((long)(PTR_0010ce70 + lVar33 + 0x10) + 8);
                          puVar2 = (undefined4 *)(PTR_0010cf10 + lVar33);
                          *puVar2 = *puVar1;
                          puVar2[1] = uVar3;
                          puVar2[2] = uVar4;
                          puVar2[3] = uVar5;
                          *(undefined8 *)(puVar27 + lVar33 + 0x10) = uVar28;
                          *(undefined8 *)((long)(puVar27 + lVar33 + 0x10) + 8) = uVar6;
                        }
                        if (uVar26 == uVar31) goto LAB_001087cc;
                        puVar27 = PTR_0010ce70 + uVar31;
                        puVar32 = PTR_0010cf10 + uVar31;
                      }
                      lVar34 = 0;
                      do {
                        puVar32[lVar34] = puVar27[lVar34];
                        lVar34 = lVar34 + 1;
                      } while ((byte)((char)uVar25 + (char)lVar34) < bVar36);
                    }
LAB_001087cc:
                    *PTR_0010cf08 = bVar36;
                  }
                  puVar32 = PTR_0010cf28;
                  puVar27 = PTR_0010ce70;
                  x2com_build_msg(PTR_0010cf28,4,PTR_0010ce70,puVar14);
                  cVar23 = x2com_get_msg_last_pos(puVar32);
                  x2com_tx_msg(param_1,param_2,puVar32,cVar23 + '\x01');
                  x2com_start_resp_timer(param_1,param_2);
                  bVar37 = *puVar14;
                  if ((bVar37 == 0) || (uVar28 = 0x13, bVar37 == DAT_0010d014)) {
                    *PTR_0010ce90 = 1;
                    uVar28 = 0x12;
                  }
                  *PTR_0010ce88 = 1;
                  if ((bVar37 == 0) || (bVar36 = *PTR_0010cf08, (ulong)bVar36 == 0))
                  goto LAB_00108a4d;
                  bVar24 = 0xe;
                  if (bVar37 < 0xe) {
                    bVar24 = bVar37;
                  }
                  uVar26 = 0;
                  bVar29 = 0;
                  do {
                    cVar23 = PTR_0010cf10[uVar26];
                    uVar31 = 1;
                    do {
                      lVar34 = uVar31 - 1;
                      if (bVar24 <= uVar31) break;
                      uVar31 = uVar31 + 1;
                    } while (cVar23 != puVar27[lVar34]);
                    if (cVar23 != puVar27[lVar34]) {
                      uVar31 = (ulong)bVar29;
                      bVar29 = bVar29 + 1;
                      acStack_46[uVar31] = cVar23;
                    }
                    uVar26 = uVar26 + 1;
                  } while (uVar26 != bVar36);
                  if (bVar29 == 0) goto LAB_00108a4d;
LAB_00108a29:
                  memcpy(PTR_0010cf10,acStack_46,(ulong)bVar29);
                }
                *PTR_0010cf08 = bVar29;
                DAT_0010d014 = bVar37;
                goto LAB_00107eb1;
              }
              __android_log_print(6,"BluetoothChatService","x2com_xmit - cwa progress");
              puVar30 = PTR_0010cef0;
              puVar32 = PTR_0010ce58;
              puVar27 = PTR_0010ce50;
              bVar37 = *PTR_0010ce58;
              if (bVar37 != 0) {
                bVar36 = 0xe;
                if (bVar37 < 0xe) {
                  bVar36 = bVar37;
                }
                if (bVar36 != 0) {
                  uVar26 = (ulong)(byte)(bVar36 - 1) + 1;
                  if (uVar26 < 0x20) {
                    uVar25 = 0;
                  }
                  else {
                    uVar25 = (uint)uVar26 & 0xffffffe0;
                    uVar31 = (ulong)uVar25;
                    lVar34 = (uVar31 - 0x20 >> 5) + 1;
                    uVar35 = (ulong)((uint)lVar34 & 1);
                    if (uVar31 - 0x20 == 0) {
                      lVar33 = 0;
                    }
                    else {
                      lVar34 = uVar35 - lVar34;
                      lVar33 = 0;
                      do {
                        puVar2 = (undefined4 *)(puVar27 + lVar33);
                        uVar3 = puVar2[1];
                        uVar4 = puVar2[2];
                        uVar5 = puVar2[3];
                        uVar28 = *(undefined8 *)(puVar27 + lVar33 + 0x10);
                        uVar6 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x10) + 8);
                        uVar7 = *(undefined8 *)(puVar27 + lVar33 + 0x20);
                        uVar8 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x20) + 8);
                        uVar9 = *(undefined8 *)(puVar27 + lVar33 + 0x30);
                        uVar10 = *(undefined8 *)((long)(puVar27 + lVar33 + 0x30) + 8);
                        puVar1 = (undefined4 *)(puVar30 + lVar33);
                        *puVar1 = *puVar2;
                        puVar1[1] = uVar3;
                        puVar1[2] = uVar4;
                        puVar1[3] = uVar5;
                        *(undefined8 *)(puVar30 + lVar33 + 0x10) = uVar28;
                        *(undefined8 *)((long)(puVar30 + lVar33 + 0x10) + 8) = uVar6;
                        *(undefined8 *)(puVar30 + lVar33 + 0x20) = uVar7;
                        *(undefined8 *)((long)(puVar30 + lVar33 + 0x20) + 8) = uVar8;
                        *(undefined8 *)(puVar30 + lVar33 + 0x30) = uVar9;
                        *(undefined8 *)((long)(puVar30 + lVar33 + 0x30) + 8) = uVar10;
                        lVar33 = lVar33 + 0x40;
                        lVar34 = lVar34 + 2;
                      } while (lVar34 != 0);
                    }
                    puVar27 = PTR_0010cef0;
                    if (uVar35 != 0) {
                      puVar1 = (undefined4 *)(PTR_0010ce50 + lVar33);
                      uVar3 = puVar1[1];
                      uVar4 = puVar1[2];
                      uVar5 = puVar1[3];
                      uVar28 = *(undefined8 *)(PTR_0010ce50 + lVar33 + 0x10);
                      uVar6 = *(undefined8 *)((long)(PTR_0010ce50 + lVar33 + 0x10) + 8);
                      puVar2 = (undefined4 *)(PTR_0010cef0 + lVar33);
                      *puVar2 = *puVar1;
                      puVar2[1] = uVar3;
                      puVar2[2] = uVar4;
                      puVar2[3] = uVar5;
                      *(undefined8 *)(puVar27 + lVar33 + 0x10) = uVar28;
                      *(undefined8 *)((long)(puVar27 + lVar33 + 0x10) + 8) = uVar6;
                    }
                    if (uVar26 == uVar31) goto LAB_001083fe;
                    puVar27 = PTR_0010ce50 + uVar31;
                    puVar30 = PTR_0010cef0 + uVar31;
                  }
                  lVar34 = 0;
                  do {
                    puVar30[lVar34] = puVar27[lVar34];
                    lVar34 = lVar34 + 1;
                  } while ((byte)((char)uVar25 + (char)lVar34) < bVar36);
                }
LAB_001083fe:
                *PTR_0010cee8 = bVar36;
              }
              puVar30 = PTR_0010cf28;
              puVar27 = PTR_0010ce50;
              x2com_build_msg(PTR_0010cf28,0,PTR_0010ce50,puVar32);
              cVar23 = x2com_get_msg_last_pos(puVar30);
              x2com_tx_msg(param_1,param_2,puVar30,cVar23 + '\x01');
              x2com_start_ack_timer(param_1,param_2);
              bVar37 = *puVar32;
              if ((bVar37 == 0) || (uVar28 = 0x11, bVar37 == DAT_0010d013)) {
                *PTR_0010ceb0 = 1;
                uVar28 = 0x10;
              }
              *puVar15 = 1;
              if ((bVar37 == 0) || (bVar36 = *PTR_0010cee8, (ulong)bVar36 == 0)) {
LAB_001086eb:
                bVar29 = 0;
              }
              else {
                bVar24 = 0xe;
                if (bVar37 < 0xe) {
                  bVar24 = bVar37;
                }
                uVar26 = 0;
                bVar29 = 0;
                do {
                  cVar23 = PTR_0010cef0[uVar26];
                  uVar31 = 1;
                  do {
                    lVar34 = uVar31 - 1;
                    if (bVar24 <= uVar31) break;
                    uVar31 = uVar31 + 1;
                  } while (cVar23 != puVar27[lVar34]);
                  if (cVar23 != puVar27[lVar34]) {
                    uVar31 = (ulong)bVar29;
                    bVar29 = bVar29 + 1;
                    acStack_46[uVar31] = cVar23;
                  }
                  uVar26 = uVar26 + 1;
                } while (uVar26 != bVar36);
                if (bVar29 == 0) goto LAB_001086eb;
LAB_001086ce:
                memcpy(PTR_0010cef0,acStack_46,(ulong)bVar29);
              }
              *PTR_0010cee8 = bVar29;
              DAT_0010d013 = bVar37;
              goto LAB_00107eb1;
            }
            *PTR_0010ced8 = 0;
            pcVar22 = DAT_0010cf38;
            puVar27 = PTR_0010cf28;
            x2com_build_msg(PTR_0010cf28,3,PTR_0010cf30,DAT_0010cf38);
            cVar23 = x2com_get_msg_last_pos(puVar27);
            x2com_tx_msg(param_1,param_2,puVar27,cVar23 + '\x01');
            cVar23 = *pcVar22;
            if (cVar23 == '\0') {
              uVar28 = 0xe;
              goto LAB_00107eb1;
            }
            *puVar18 = 1;
          }
          else {
            x2com_build_msg(PTR_0010cf28,3,PTR_0010cf30,DAT_0010cf38);
            cVar23 = x2com_get_msg_last_pos(puVar21);
            x2com_tx_msg(param_1,param_2,puVar21,cVar23 + '\x01');
            cVar23 = *pcVar22;
            if ((cVar23 == '\0') || (cVar23 == DAT_0010d012)) {
              *puVar18 = 0;
              uVar28 = 0xe;
              goto LAB_00107eb1;
            }
          }
          uVar28 = 0xf;
          DAT_0010d012 = cVar23;
          goto LAB_00107eb1;
        }
        *PTR_0010ce20 = 0;
        puVar30 = PTR_0010cf28;
        puVar32 = PTR_0010ce38;
        x2com_build_msg(PTR_0010cf28,1,PTR_0010ce30,PTR_0010ce38);
        cVar23 = x2com_get_msg_last_pos(puVar30);
        x2com_tx_msg(param_1,param_2,puVar30,cVar23 + '\x01');
        cVar23 = *puVar32;
        if (cVar23 == '\0') {
          uVar28 = 0xc;
          goto LAB_00107eb1;
        }
        *puVar27 = 1;
      }
      else {
        x2com_build_msg(PTR_0010cf28,1,PTR_0010ce30,PTR_0010ce38);
        cVar23 = x2com_get_msg_last_pos(puVar21);
        x2com_tx_msg(param_1,param_2,puVar21,cVar23 + '\x01');
        cVar23 = *puVar32;
        if ((cVar23 == '\0') || (cVar23 == DAT_0010d011)) {
          *puVar27 = 0;
          uVar28 = 0xc;
          goto LAB_00107eb1;
        }
      }
      uVar28 = 0xd;
      DAT_0010d011 = cVar23;
      goto LAB_00107eb1;
    }
    *PTR_0010cec0 = 0;
    puVar32 = PTR_0010cf28;
    puVar27 = PTR_0010cf20;
    x2com_build_msg(PTR_0010cf28,5,PTR_0010cf18,PTR_0010cf20);
    cVar23 = x2com_get_msg_last_pos(puVar32);
    x2com_tx_msg(param_1,param_2,puVar32,cVar23 + '\x01');
    cVar23 = *puVar27;
    if (cVar23 == '\0') {
      uVar28 = 10;
      goto LAB_00107eb1;
    }
    *puVar16 = 1;
  }
  else {
    x2com_build_msg(PTR_0010cf28,5,PTR_0010cf18,PTR_0010cf20);
    cVar23 = x2com_get_msg_last_pos(puVar21);
    x2com_tx_msg(param_1,param_2,puVar21,cVar23 + '\x01');
    cVar23 = *puVar20;
    if ((cVar23 == '\0') || (cVar23 == DAT_0010d010)) {
      *puVar16 = 0;
      uVar28 = 10;
      goto LAB_00107eb1;
    }
  }
  uVar28 = 0xb;
  DAT_0010d010 = cVar23;
LAB_00107eb1:
  if (*(long *)(in_FS_OFFSET + 0x28) != lStack_38) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return uVar28;
}

