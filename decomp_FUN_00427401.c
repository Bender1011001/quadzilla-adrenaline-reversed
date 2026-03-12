// FUN_00427401 @ 00427401


undefined4 FUN_00427401(int *param_1)

{
  ushort *puVar1;
  uint *puVar2;
  undefined1 uVar3;
  ushort uVar4;
  int iVar5;
  char cVar6;
  int *piVar7;
  undefined4 uVar8;
  int *piVar9;
  int iVar10;
  undefined1 *puVar11;
  int *piVar12;
  int iVar13;
  byte bVar14;
  uint uVar15;
  int iVar16;
  int *piVar17;
  int *piVar18;
  int iVar19;
  uint uVar20;
  int iVar21;
  byte *pbVar22;
  bool bVar23;
  int local_78 [2];
  int local_70;
  int local_6c;
  int local_68;
  int local_64;
  uint local_60;
  uint local_5c;
  uint local_58;
  int *local_54;
  int local_50;
  int local_4c;
  int local_48;
  int local_44;
  int *local_40;
  int *local_3c;
  int *local_38;
  uint local_34;
  int local_30;
  uint local_2c;
  uint local_28;
  uint local_24;
  int local_20;
  uint local_1c;
  uint local_18;
  int local_14;
  int local_10;
  int local_c;
  uint local_8;
  
  piVar7 = param_1;
  uVar8 = 0;
  iVar13 = *param_1;
  if (param_1[1] == 10) {
    param_1[0x3e85] = 0;
    param_1[0x3e86] = 0;
    param_1[0x3e87] = 0;
    param_1[0x3e88] = 0;
    param_1[0x3e89] = 0;
    param_1[0x3e8a] = 0;
    param_1[0x3e8b] = 0;
    param_1[0x3e8c] = 0;
    param_1[0x3e8d] = 0;
    param_1[0x3e8e] = 0;
    param_1[0x3e8f] = 0;
    param_1[0x3e90] = 0;
    param_1[0x3e91] = 0;
    param_1[0x3e92] = 0;
    param_1[0x3e93] = 0;
    param_1[0x3e94] = 0;
    param_1[0x3e95] = 0;
    param_1[0x3e96] = 0;
    param_1[0x3e97] = 0;
    param_1[0x3e98] = 0;
    param_1[0x3e99] = 0;
    param_1[0x3e9a] = 0;
    param_1[0x3e9b] = 0;
    param_1[0x3e9c] = 0;
  }
  local_8 = param_1[0x3e85];
  local_18 = param_1[0x3e86];
  local_28 = param_1[0x3e87];
  local_44 = param_1[0x3e88];
  local_2c = param_1[0x3e89];
  local_34 = param_1[0x3e8a];
  local_60 = param_1[0x3e8b];
  local_48 = param_1[0x3e8c];
  local_20 = param_1[0x3e8d];
  local_30 = param_1[0x3e8e];
  local_54 = (int *)param_1[0x3e8f];
  local_14 = param_1[0x3e90];
  local_10 = param_1[0x3e91];
  local_4c = param_1[0x3e92];
  local_24 = param_1[0x3e93];
  iVar5 = param_1[0x3e94];
  local_c = param_1[0x3e95];
  local_1c = param_1[0x3e96];
  local_58 = param_1[0x3e97];
  local_5c = param_1[0x3e98];
  local_50 = param_1[0x3e99];
  local_38 = (int *)param_1[0x3e9a];
  local_3c = (int *)param_1[0x3e9b];
  local_40 = (int *)param_1[0x3e9c];
  switch(param_1[1]) {
  case 10:
    param_1[1] = 10;
    while (param_1[8] < 8) {
      piVar12 = (int *)*param_1;
      if (piVar12[1] == 0) goto LAB_00428c4d;
      param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
      param_1[8] = param_1[8] + 8;
      *piVar12 = *piVar12 + 1;
      *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
      *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
      if (*(int *)(*param_1 + 8) == 0) {
        piVar12 = (int *)(*param_1 + 0xc);
        *piVar12 = *piVar12 + 1;
      }
    }
    iVar10 = param_1[8];
    param_1[8] = iVar10 + -8;
    if ((char)((uint)param_1[7] >> ((char)iVar10 - 8U & 0x1f)) == 'B')
    goto switchD_00427597_caseD_b;
    goto LAB_004277be;
  case 0xb:
switchD_00427597_caseD_b:
    param_1[1] = 0xb;
    while (param_1[8] < 8) {
      piVar12 = (int *)*param_1;
      if (piVar12[1] == 0) goto LAB_00428c4d;
      param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
      param_1[8] = param_1[8] + 8;
      *piVar12 = *piVar12 + 1;
      *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
      *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
      if (*(int *)(*param_1 + 8) == 0) {
        piVar12 = (int *)(*param_1 + 0xc);
        *piVar12 = *piVar12 + 1;
      }
    }
    iVar10 = param_1[8];
    param_1[8] = iVar10 + -8;
    if ((char)((uint)param_1[7] >> ((char)iVar10 - 8U & 0x1f)) == 'Z')
    goto switchD_00427597_caseD_c;
    goto LAB_004277be;
  case 0xc:
switchD_00427597_caseD_c:
    param_1[1] = 0xc;
    while (param_1[8] < 8) {
      piVar12 = (int *)*param_1;
      if (piVar12[1] == 0) goto LAB_00428c4d;
      param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
      param_1[8] = param_1[8] + 8;
      *piVar12 = *piVar12 + 1;
      *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
      *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
      if (*(int *)(*param_1 + 8) == 0) {
        piVar12 = (int *)(*param_1 + 0xc);
        *piVar12 = *piVar12 + 1;
      }
    }
    iVar10 = param_1[8];
    param_1[8] = iVar10 + -8;
    if ((char)((uint)param_1[7] >> ((char)iVar10 - 8U & 0x1f)) == 'h')
    goto switchD_00427597_caseD_d;
    goto LAB_004277be;
  case 0xd:
switchD_00427597_caseD_d:
    param_1[1] = 0xd;
    while (param_1[8] < 8) {
      piVar12 = (int *)*param_1;
      if (piVar12[1] == 0) goto LAB_00428c4d;
      param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
      param_1[8] = param_1[8] + 8;
      *piVar12 = *piVar12 + 1;
      *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
      *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
      if (*(int *)(*param_1 + 8) == 0) {
        piVar12 = (int *)(*param_1 + 0xc);
        *piVar12 = *piVar12 + 1;
      }
    }
    iVar10 = param_1[8];
    param_1[8] = iVar10 + -8;
    uVar15 = (uint)param_1[7] >> ((char)iVar10 - 8U & 0x1f) & 0xff;
    param_1[9] = uVar15;
    if ((0x30 < uVar15) && (uVar15 < 0x3a)) {
      iVar10 = uVar15 - 0x30;
      param_1[9] = iVar10;
      if ((char)param_1[10] == '\0') {
        iVar13 = (**(code **)(iVar13 + 0x24))(*(undefined4 *)(iVar13 + 0x2c),iVar10 * 400000,1);
        param_1[0x313] = iVar13;
LAB_004277b3:
        if (iVar13 != 0) goto switchD_00427597_caseD_e;
      }
      else {
        iVar10 = (**(code **)(iVar13 + 0x24))(*(undefined4 *)(iVar13 + 0x2c),iVar10 * 200000);
        param_1[0x314] = iVar10;
        iVar13 = (**(code **)(iVar13 + 0x24))
                           (*(undefined4 *)(iVar13 + 0x2c),param_1[9] * 100000 + 1 >> 1,1);
        param_1[0x315] = iVar13;
        if (param_1[0x314] != 0) goto LAB_004277b3;
      }
      uVar8 = 0xfffffffd;
      goto switchD_00427597_default;
    }
LAB_004277be:
    uVar8 = 0xfffffffb;
    goto switchD_00427597_default;
  case 0xe:
switchD_00427597_caseD_e:
    param_1[1] = 0xe;
    while (param_1[8] < 8) {
      piVar12 = (int *)*param_1;
      if (piVar12[1] == 0) goto LAB_00428c4d;
      param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
      param_1[8] = param_1[8] + 8;
      *piVar12 = *piVar12 + 1;
      *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
      *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
      if (*(int *)(*param_1 + 8) == 0) {
        piVar12 = (int *)(*param_1 + 0xc);
        *piVar12 = *piVar12 + 1;
      }
    }
    iVar13 = param_1[8];
    param_1[8] = iVar13 + -8;
    cVar6 = (char)((uint)param_1[7] >> ((char)iVar13 - 8U & 0x1f));
    if (cVar6 != '\x17') {
      iVar13 = local_48;
      if (cVar6 == '1') goto switchD_00427597_caseD_f;
      break;
    }
  case 0x2a:
    param_1[1] = 0x2a;
    while (param_1[8] < 8) {
      piVar12 = (int *)*param_1;
      if (piVar12[1] == 0) goto LAB_00428c4d;
      param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
      param_1[8] = param_1[8] + 8;
      *piVar12 = *piVar12 + 1;
      *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
      *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
      if (*(int *)(*param_1 + 8) == 0) {
        piVar12 = (int *)(*param_1 + 0xc);
        *piVar12 = *piVar12 + 1;
      }
    }
    iVar10 = param_1[8];
    param_1[8] = iVar10 + -8;
    iVar13 = local_48;
    if ((char)((uint)param_1[7] >> ((char)iVar10 - 8U & 0x1f)) == 'r') {
switchD_00427597_caseD_2b:
      param_1[1] = 0x2b;
      while (param_1[8] < 8) {
        piVar12 = (int *)*param_1;
        if (piVar12[1] == 0) goto LAB_00428c4d;
        param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
        param_1[8] = param_1[8] + 8;
        *piVar12 = *piVar12 + 1;
        *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
        *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
        if (*(int *)(*param_1 + 8) == 0) {
          piVar12 = (int *)(*param_1 + 0xc);
          *piVar12 = *piVar12 + 1;
        }
      }
      iVar10 = param_1[8];
      param_1[8] = iVar10 + -8;
      iVar13 = local_48;
      if ((char)((uint)param_1[7] >> ((char)iVar10 - 8U & 0x1f)) == 'E') {
switchD_00427597_caseD_2c:
        param_1[1] = 0x2c;
        while (param_1[8] < 8) {
          piVar12 = (int *)*param_1;
          if (piVar12[1] == 0) goto LAB_00428c4d;
          param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
          param_1[8] = param_1[8] + 8;
          *piVar12 = *piVar12 + 1;
          *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
          *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
          if (*(int *)(*param_1 + 8) == 0) {
            piVar12 = (int *)(*param_1 + 0xc);
            *piVar12 = *piVar12 + 1;
          }
        }
        iVar10 = param_1[8];
        param_1[8] = iVar10 + -8;
        iVar13 = local_48;
        if ((char)((uint)param_1[7] >> ((char)iVar10 - 8U & 0x1f)) == '8') {
switchD_00427597_caseD_2d:
          param_1[1] = 0x2d;
          while (param_1[8] < 8) {
            piVar12 = (int *)*param_1;
            if (piVar12[1] == 0) goto LAB_00428c4d;
            param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
            param_1[8] = param_1[8] + 8;
            *piVar12 = *piVar12 + 1;
            *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
            *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
            if (*(int *)(*param_1 + 8) == 0) {
              piVar12 = (int *)(*param_1 + 0xc);
              *piVar12 = *piVar12 + 1;
            }
          }
          iVar10 = param_1[8];
          param_1[8] = iVar10 + -8;
          iVar13 = local_48;
          if ((char)((uint)param_1[7] >> ((char)iVar10 - 8U & 0x1f)) == 'P') {
switchD_00427597_caseD_2e:
            param_1[1] = 0x2e;
            while (param_1[8] < 8) {
              piVar12 = (int *)*param_1;
              if (piVar12[1] == 0) goto LAB_00428c4d;
              param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
              param_1[8] = param_1[8] + 8;
              *piVar12 = *piVar12 + 1;
              *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
              *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
              if (*(int *)(*param_1 + 8) == 0) {
                piVar12 = (int *)(*param_1 + 0xc);
                *piVar12 = *piVar12 + 1;
              }
            }
            iVar10 = param_1[8];
            param_1[8] = iVar10 + -8;
            iVar13 = local_48;
            if ((char)((uint)param_1[7] >> ((char)iVar10 - 8U & 0x1f)) == -0x70) {
              param_1[0x317] = 0;
switchD_00427597_caseD_2f:
              param_1[1] = 0x2f;
              while (param_1[8] < 8) {
                piVar12 = (int *)*param_1;
                if (piVar12[1] == 0) goto LAB_00428c4d;
                param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
                param_1[8] = param_1[8] + 8;
                *piVar12 = *piVar12 + 1;
                *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
                *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
                if (*(int *)(*param_1 + 8) == 0) {
                  piVar12 = (int *)(*param_1 + 0xc);
                  *piVar12 = *piVar12 + 1;
                }
              }
              iVar13 = param_1[8];
              param_1[8] = iVar13 + -8;
              param_1[0x317] =
                   param_1[0x317] << 8 | (uint)param_1[7] >> ((char)iVar13 - 8U & 0x1f) & 0xff;
              goto switchD_00427597_caseD_30;
            }
          }
        }
      }
    }
    break;
  case 0xf:
switchD_00427597_caseD_f:
    param_1[1] = 0xf;
    while (param_1[8] < 8) {
      piVar12 = (int *)*param_1;
      if (piVar12[1] == 0) goto LAB_00428c4d;
      param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
      param_1[8] = param_1[8] + 8;
      *piVar12 = *piVar12 + 1;
      *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
      *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
      if (*(int *)(*param_1 + 8) == 0) {
        piVar12 = (int *)(*param_1 + 0xc);
        *piVar12 = *piVar12 + 1;
      }
    }
    iVar10 = param_1[8];
    param_1[8] = iVar10 + -8;
    iVar13 = local_48;
    if ((char)((uint)param_1[7] >> ((char)iVar10 - 8U & 0x1f)) == 'A')
    goto switchD_00427597_caseD_10;
    break;
  case 0x10:
switchD_00427597_caseD_10:
    param_1[1] = 0x10;
    while (param_1[8] < 8) {
      piVar12 = (int *)*param_1;
      if (piVar12[1] == 0) goto LAB_00428c4d;
      param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
      param_1[8] = param_1[8] + 8;
      *piVar12 = *piVar12 + 1;
      *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
      *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
      if (*(int *)(*param_1 + 8) == 0) {
        piVar12 = (int *)(*param_1 + 0xc);
        *piVar12 = *piVar12 + 1;
      }
    }
    iVar10 = param_1[8];
    param_1[8] = iVar10 + -8;
    iVar13 = local_48;
    if ((char)((uint)param_1[7] >> ((char)iVar10 - 8U & 0x1f)) == 'Y')
    goto switchD_00427597_caseD_11;
    break;
  case 0x11:
switchD_00427597_caseD_11:
    param_1[1] = 0x11;
    while (param_1[8] < 8) {
      piVar12 = (int *)*param_1;
      if (piVar12[1] == 0) goto LAB_00428c4d;
      param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
      param_1[8] = param_1[8] + 8;
      *piVar12 = *piVar12 + 1;
      *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
      *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
      if (*(int *)(*param_1 + 8) == 0) {
        piVar12 = (int *)(*param_1 + 0xc);
        *piVar12 = *piVar12 + 1;
      }
    }
    iVar10 = param_1[8];
    param_1[8] = iVar10 + -8;
    iVar13 = local_48;
    if ((char)((uint)param_1[7] >> ((char)iVar10 - 8U & 0x1f)) == '&')
    goto switchD_00427597_caseD_12;
    break;
  case 0x12:
switchD_00427597_caseD_12:
    param_1[1] = 0x12;
    while (param_1[8] < 8) {
      piVar12 = (int *)*param_1;
      if (piVar12[1] == 0) goto LAB_00428c4d;
      param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
      param_1[8] = param_1[8] + 8;
      *piVar12 = *piVar12 + 1;
      *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
      *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
      if (*(int *)(*param_1 + 8) == 0) {
        piVar12 = (int *)(*param_1 + 0xc);
        *piVar12 = *piVar12 + 1;
      }
    }
    iVar10 = param_1[8];
    param_1[8] = iVar10 + -8;
    iVar13 = local_48;
    if ((char)((uint)param_1[7] >> ((char)iVar10 - 8U & 0x1f)) == 'S')
    goto switchD_00427597_caseD_13;
    break;
  case 0x13:
switchD_00427597_caseD_13:
    param_1[1] = 0x13;
    while (param_1[8] < 8) {
      piVar12 = (int *)*param_1;
      if (piVar12[1] == 0) goto LAB_00428c4d;
      param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
      param_1[8] = param_1[8] + 8;
      *piVar12 = *piVar12 + 1;
      *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
      *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
      if (*(int *)(*param_1 + 8) == 0) {
        piVar12 = (int *)(*param_1 + 0xc);
        *piVar12 = *piVar12 + 1;
      }
    }
    iVar10 = param_1[8];
    param_1[8] = iVar10 + -8;
    iVar13 = local_48;
    if ((char)((uint)param_1[7] >> ((char)iVar10 - 8U & 0x1f)) == 'Y') {
      param_1[0xb] = param_1[0xb] + 1;
      param_1[0x316] = 0;
      goto switchD_00427597_caseD_14;
    }
    break;
  case 0x14:
switchD_00427597_caseD_14:
    param_1[1] = 0x14;
    while (param_1[8] < 8) {
      piVar12 = (int *)*param_1;
      if (piVar12[1] == 0) goto LAB_00428c4d;
      param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
      param_1[8] = param_1[8] + 8;
      *piVar12 = *piVar12 + 1;
      *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
      *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
      if (*(int *)(*param_1 + 8) == 0) {
        piVar12 = (int *)(*param_1 + 0xc);
        *piVar12 = *piVar12 + 1;
      }
    }
    iVar13 = param_1[8];
    param_1[8] = iVar13 + -8;
    param_1[0x316] = param_1[0x316] << 8 | (uint)param_1[7] >> ((char)iVar13 - 8U & 0x1f) & 0xff;
  case 0x15:
    param_1[1] = 0x15;
    while (param_1[8] < 8) {
      piVar12 = (int *)*param_1;
      if (piVar12[1] == 0) goto LAB_00428c4d;
      param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
      param_1[8] = param_1[8] + 8;
      *piVar12 = *piVar12 + 1;
      *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
      *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
      if (*(int *)(*param_1 + 8) == 0) {
        piVar12 = (int *)(*param_1 + 0xc);
        *piVar12 = *piVar12 + 1;
      }
    }
    iVar13 = param_1[8];
    param_1[8] = iVar13 + -8;
    param_1[0x316] = param_1[0x316] << 8 | (uint)param_1[7] >> ((char)iVar13 - 8U & 0x1f) & 0xff;
switchD_00427597_caseD_16:
    param_1[1] = 0x16;
    while (param_1[8] < 8) {
      piVar12 = (int *)*param_1;
      if (piVar12[1] == 0) goto LAB_00428c4d;
      param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
      param_1[8] = param_1[8] + 8;
      *piVar12 = *piVar12 + 1;
      *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
      *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
      if (*(int *)(*param_1 + 8) == 0) {
        piVar12 = (int *)(*param_1 + 0xc);
        *piVar12 = *piVar12 + 1;
      }
    }
    iVar13 = param_1[8];
    param_1[8] = iVar13 + -8;
    param_1[0x316] = param_1[0x316] << 8 | (uint)param_1[7] >> ((char)iVar13 - 8U & 0x1f) & 0xff;
switchD_00427597_caseD_17:
    param_1[1] = 0x17;
    while (param_1[8] < 8) {
      piVar12 = (int *)*param_1;
      if (piVar12[1] == 0) goto LAB_00428c4d;
      param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
      param_1[8] = param_1[8] + 8;
      *piVar12 = *piVar12 + 1;
      *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
      *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
      if (*(int *)(*param_1 + 8) == 0) {
        piVar12 = (int *)(*param_1 + 0xc);
        *piVar12 = *piVar12 + 1;
      }
    }
    iVar13 = param_1[8];
    param_1[8] = iVar13 + -8;
    param_1[0x316] = param_1[0x316] << 8 | (uint)param_1[7] >> ((char)iVar13 - 8U & 0x1f) & 0xff;
switchD_00427597_caseD_18:
    param_1[1] = 0x18;
    while (param_1[8] < 1) {
      piVar12 = (int *)*param_1;
      if (piVar12[1] == 0) goto LAB_00428c4d;
      param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
      param_1[8] = param_1[8] + 8;
      *piVar12 = *piVar12 + 1;
      *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
      *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
      if (*(int *)(*param_1 + 8) == 0) {
        piVar12 = (int *)(*param_1 + 0xc);
        *piVar12 = *piVar12 + 1;
      }
    }
    iVar13 = param_1[8];
    param_1[0xd] = 0;
    param_1[8] = iVar13 + -1;
    *(byte *)(param_1 + 4) = (byte)((uint)param_1[7] >> ((char)iVar13 - 1U & 0x1f)) & 1;
switchD_00427597_caseD_19:
    param_1[1] = 0x19;
    while (param_1[8] < 8) {
      piVar12 = (int *)*param_1;
      if (piVar12[1] == 0) goto LAB_00428c4d;
      param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
      param_1[8] = param_1[8] + 8;
      *piVar12 = *piVar12 + 1;
      *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
      *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
      if (*(int *)(*param_1 + 8) == 0) {
        piVar12 = (int *)(*param_1 + 0xc);
        *piVar12 = *piVar12 + 1;
      }
    }
    iVar13 = param_1[8];
    param_1[8] = iVar13 + -8;
    param_1[0xd] = param_1[0xd] << 8 | (uint)param_1[7] >> ((char)iVar13 - 8U & 0x1f) & 0xff;
switchD_00427597_caseD_1a:
    param_1[1] = 0x1a;
    while (param_1[8] < 8) {
      piVar12 = (int *)*param_1;
      if (piVar12[1] == 0) goto LAB_00428c4d;
      param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
      param_1[8] = param_1[8] + 8;
      *piVar12 = *piVar12 + 1;
      *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
      *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
      if (*(int *)(*param_1 + 8) == 0) {
        piVar12 = (int *)(*param_1 + 0xc);
        *piVar12 = *piVar12 + 1;
      }
    }
    iVar13 = param_1[8];
    param_1[8] = iVar13 + -8;
    param_1[0xd] = param_1[0xd] << 8 | (uint)param_1[7] >> ((char)iVar13 - 8U & 0x1f) & 0xff;
switchD_00427597_caseD_1b:
    param_1[1] = 0x1b;
    while (param_1[8] < 8) {
      piVar12 = (int *)*param_1;
      if (piVar12[1] == 0) goto LAB_00428c4d;
      param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
      param_1[8] = param_1[8] + 8;
      *piVar12 = *piVar12 + 1;
      *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
      *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
      if (*(int *)(*param_1 + 8) == 0) {
        piVar12 = (int *)(*param_1 + 0xc);
        *piVar12 = *piVar12 + 1;
      }
    }
    iVar13 = param_1[8];
    param_1[8] = iVar13 + -8;
    uVar15 = param_1[0xd] << 8 | (uint)param_1[7] >> ((char)iVar13 - 8U & 0x1f) & 0xff;
    param_1[0xd] = uVar15;
    iVar13 = local_48;
    if ((-1 < (int)uVar15) && ((int)uVar15 <= param_1[9] * 100000 + 10)) {
      for (local_8 = 0; (int)local_8 < 0x10; local_8 = local_8 + 1) {
switchD_00427597_caseD_1c:
        param_1[1] = 0x1c;
        while (param_1[8] < 1) {
          piVar12 = (int *)*param_1;
          if (piVar12[1] == 0) goto LAB_00428c4d;
          param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
          param_1[8] = param_1[8] + 8;
          *piVar12 = *piVar12 + 1;
          *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
          *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
          if (*(int *)(*param_1 + 8) == 0) {
            piVar12 = (int *)(*param_1 + 0xc);
            *piVar12 = *piVar12 + 1;
          }
        }
        iVar13 = param_1[8];
        param_1[8] = iVar13 + -1;
        if (((byte)((uint)param_1[7] >> ((char)iVar13 - 1U & 0x1f)) & 1) == 1) {
          *(undefined1 *)(local_8 + 0xd6c + (int)param_1) = 1;
        }
        else {
          *(undefined1 *)(local_8 + 0xd6c + (int)param_1) = 0;
        }
      }
      local_8 = 0;
      piVar12 = param_1 + 0x31b;
      for (iVar13 = 0x40; iVar13 != 0; iVar13 = iVar13 + -1) {
        *piVar12 = 0;
        piVar12 = piVar12 + 1;
      }
      for (; (int)local_8 < 0x10; local_8 = local_8 + 1) {
        if (*(char *)(local_8 + 0xd6c + (int)param_1) != '\0') {
          for (local_18 = 0; (int)local_18 < 0x10; local_18 = local_18 + 1) {
switchD_00427597_caseD_1d:
            param_1[1] = 0x1d;
            while (param_1[8] < 1) {
              piVar12 = (int *)*param_1;
              if (piVar12[1] == 0) goto LAB_00428c4d;
              param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
              param_1[8] = param_1[8] + 8;
              *piVar12 = *piVar12 + 1;
              *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
              *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
              if (*(int *)(*param_1 + 8) == 0) {
                piVar12 = (int *)(*param_1 + 0xc);
                *piVar12 = *piVar12 + 1;
              }
            }
            iVar13 = param_1[8];
            param_1[8] = iVar13 + -1;
            if (((byte)((uint)param_1[7] >> ((char)iVar13 - 1U & 0x1f)) & 1) == 1) {
              *(undefined1 *)(local_8 * 0x10 + local_18 + 0xc6c + (int)param_1) = 1;
            }
          }
        }
      }
      FUN_004292a0((int)param_1);
      iVar13 = local_48;
      if (param_1[0x31a] != 0) {
        local_44 = param_1[0x31a] + 2;
switchD_00427597_caseD_1e:
        param_1[1] = 0x1e;
        while (param_1[8] < 3) {
          piVar12 = (int *)*param_1;
          if (piVar12[1] == 0) goto LAB_00428c4d;
          param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
          param_1[8] = param_1[8] + 8;
          *piVar12 = *piVar12 + 1;
          *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
          *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
          if (*(int *)(*param_1 + 8) == 0) {
            piVar12 = (int *)(*param_1 + 0xc);
            *piVar12 = *piVar12 + 1;
          }
        }
        iVar13 = param_1[8];
        param_1[8] = iVar13 + -3;
        local_2c = (uint)param_1[7] >> ((char)iVar13 - 3U & 0x1f) & 7;
        iVar13 = local_48;
        if ((1 < local_2c) && (local_2c < 7)) {
switchD_00427597_caseD_1f:
          param_1[1] = 0x1f;
          while (param_1[8] < 0xf) {
            piVar12 = (int *)*param_1;
            if (piVar12[1] == 0) goto LAB_00428c4d;
            param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
            param_1[8] = param_1[8] + 8;
            *piVar12 = *piVar12 + 1;
            *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
            *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
            if (*(int *)(*param_1 + 8) == 0) {
              piVar12 = (int *)(*param_1 + 0xc);
              *piVar12 = *piVar12 + 1;
            }
          }
          iVar13 = param_1[8];
          param_1[8] = iVar13 + -0xf;
          local_34 = (uint)param_1[7] >> ((char)iVar13 - 0xfU & 0x1f) & 0x7fff;
          iVar13 = local_48;
          if (local_34 != 0) {
            local_8 = 0;
            while (uVar15 = local_34, (int)local_8 < (int)local_34) {
              local_18 = 0;
switchD_00427597_caseD_20:
              while( true ) {
                param_1[1] = 0x20;
                while (param_1[8] < 1) {
                  piVar12 = (int *)*param_1;
                  if (piVar12[1] == 0) goto LAB_00428c4d;
                  param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
                  param_1[8] = param_1[8] + 8;
                  *piVar12 = *piVar12 + 1;
                  *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
                  *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
                  if (*(int *)(*param_1 + 8) == 0) {
                    piVar12 = (int *)(*param_1 + 0xc);
                    *piVar12 = *piVar12 + 1;
                  }
                }
                iVar13 = param_1[8];
                param_1[8] = iVar13 + -1;
                if (((uint)param_1[7] >> ((char)iVar13 - 1U & 0x1f) & 1) == 0) break;
                local_18 = local_18 + 1;
                iVar13 = local_48;
                if ((int)local_2c <= (int)local_18) goto LAB_00428f47;
              }
              *(undefined1 *)(local_8 + 0x650e + (int)param_1) = (undefined1)local_18;
              local_8 = local_8 + 1;
            }
            bVar14 = 0;
            if (0 < (int)local_2c) {
              uVar20 = 0;
              do {
                *(byte *)((int)local_78 + uVar20) = bVar14;
                bVar14 = bVar14 + 1;
                uVar20 = (uint)bVar14;
              } while ((int)uVar20 < (int)local_2c);
            }
            local_8 = 0;
            if (0 < (int)uVar15) {
              do {
                bVar14 = *(byte *)((int)param_1 + local_8 + 0x650e);
                uVar15 = (uint)bVar14;
                uVar3 = *(undefined1 *)((int)local_78 + uVar15);
                puVar11 = (undefined1 *)((int)local_78 + uVar15);
                if (bVar14 != 0) {
                  do {
                    *puVar11 = puVar11[-1];
                    uVar15 = uVar15 - 1;
                    puVar11 = puVar11 + -1;
                  } while (uVar15 != 0);
                }
                local_78[0] = CONCAT31(local_78[0]._1_3_,uVar3);
                *(undefined1 *)(local_8 + 0x1ebc + (int)param_1) = uVar3;
                local_8 = local_8 + 1;
              } while ((int)local_8 < (int)local_34);
            }
            for (local_28 = 0; (int)local_28 < (int)local_2c; local_28 = local_28 + 1) {
switchD_00427597_caseD_21:
              param_1[1] = 0x21;
              while (param_1[8] < 5) {
                piVar12 = (int *)*param_1;
                if (piVar12[1] == 0) goto LAB_00428c4d;
                param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
                param_1[8] = param_1[8] + 8;
                *piVar12 = *piVar12 + 1;
                *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
                *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
                if (*(int *)(*param_1 + 8) == 0) {
                  piVar12 = (int *)(*param_1 + 0xc);
                  *piVar12 = *piVar12 + 1;
                }
              }
              iVar13 = param_1[8];
              param_1[8] = iVar13 + -5;
              local_24 = (uint)param_1[7] >> ((char)iVar13 - 5U & 0x1f) & 0x1f;
              local_8 = 0;
              while ((int)local_8 < local_44) {
                while( true ) {
                  iVar13 = local_48;
                  if (((int)local_24 < 1) || (0x14 < (int)local_24)) goto LAB_00428f47;
switchD_00427597_caseD_22:
                  param_1[1] = 0x22;
                  while (param_1[8] < 1) {
                    piVar12 = (int *)*param_1;
                    if (piVar12[1] == 0) goto LAB_00428c4d;
                    param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
                    param_1[8] = param_1[8] + 8;
                    *piVar12 = *piVar12 + 1;
                    *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
                    *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
                    if (*(int *)(*param_1 + 8) == 0) {
                      piVar12 = (int *)(*param_1 + 0xc);
                      *piVar12 = *piVar12 + 1;
                    }
                  }
                  iVar13 = param_1[8];
                  param_1[8] = iVar13 + -1;
                  if (((uint)param_1[7] >> ((char)iVar13 - 1U & 0x1f) & 1) == 0) break;
switchD_00427597_caseD_23:
                  param_1[1] = 0x23;
                  while (param_1[8] < 1) {
                    piVar12 = (int *)*param_1;
                    if (piVar12[1] == 0) goto LAB_00428c4d;
                    param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
                    param_1[8] = param_1[8] + 8;
                    *piVar12 = *piVar12 + 1;
                    *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
                    *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
                    if (*(int *)(*param_1 + 8) == 0) {
                      piVar12 = (int *)(*param_1 + 0xc);
                      *piVar12 = *piVar12 + 1;
                    }
                  }
                  iVar13 = param_1[8];
                  param_1[8] = iVar13 + -1;
                  if (((uint)param_1[7] >> ((char)iVar13 - 1U & 0x1f) & 1) == 0) {
                    local_24 = local_24 + 1;
                  }
                  else {
                    local_24 = local_24 - 1;
                  }
                }
                iVar13 = local_28 * 0x102 + local_8;
                local_8 = local_8 + 1;
                *(undefined1 *)(iVar13 + 0xab60 + (int)param_1) = (undefined1)local_24;
              }
            }
            local_28 = 0;
            if (0 < (int)local_2c) {
              local_54 = param_1 + 0x2ad8;
              piVar12 = param_1 + 15999;
              piVar17 = param_1 + 0x3267;
              local_60 = local_2c;
              local_28 = local_2c;
              do {
                piVar18 = (int *)0x0;
                iVar13 = 0;
                param_1 = (int *)0x20;
                if (0 < local_44) {
                  do {
                    piVar9 = (int *)(uint)*(byte *)((int)local_54 + iVar13);
                    if (piVar18 < piVar9) {
                      piVar18 = piVar9;
                    }
                    if (piVar9 < param_1) {
                      param_1 = piVar9;
                    }
                    iVar13 = iVar13 + 1;
                  } while (iVar13 < local_44);
                }
                FUN_0042c706(piVar17 + -0x60c,piVar17,(int)(piVar17 + 0x60c),(int)local_54,
                             (uint)param_1,(int)piVar18,local_44);
                local_54 = (int *)((int)local_54 + 0x102);
                *piVar12 = (int)param_1;
                piVar12 = piVar12 + 1;
                piVar17 = piVar17 + 0x102;
                local_60 = local_60 - 1;
              } while (local_60 != 0);
            }
            local_20 = 0;
            local_60 = piVar7[0x31a] + 1;
            local_54 = (int *)(piVar7[9] * 100000);
            piVar12 = piVar7 + 0x10;
            for (iVar13 = 0x100; iVar13 != 0; iVar13 = iVar13 + -1) {
              *piVar12 = 0;
              piVar12 = piVar12 + 1;
            }
            local_8 = 0x100;
            iVar10 = 0xfff;
            iVar13 = 0xf;
            piVar12 = piVar7 + 0x7ae;
            do {
              param_1 = (int *)0xf;
              do {
                iVar21 = iVar10;
                *(char *)(iVar21 + 0xe7c + (int)piVar7) = (char)param_1 + (char)iVar13 * '\x10';
                iVar10 = iVar21 + -1;
                param_1 = (int *)((int)param_1 + -1);
              } while (-1 < (int)param_1);
              iVar13 = iVar13 + -1;
              *piVar12 = iVar21;
              piVar12 = piVar12 + -1;
            } while (-1 < iVar13);
            local_14 = 0;
            local_48 = 0;
            iVar13 = local_48;
            if (0 < (int)local_34) {
              local_5c = (uint)*(byte *)(piVar7 + 0x7af);
              local_20 = 0x31;
              local_50 = piVar7[local_5c + 15999];
              local_38 = piVar7 + local_5c * 0x102 + 0x2c5b;
              local_40 = piVar7 + local_5c * 0x102 + 0x3873;
              local_3c = piVar7 + local_5c * 0x102 + 0x3267;
              local_c = local_50;
switchD_00427597_caseD_24:
              piVar7[1] = 0x24;
              while (piVar7[8] < local_c) {
                piVar12 = (int *)*piVar7;
                if (piVar12[1] == 0) goto LAB_00428c4d;
                piVar7[7] = piVar7[7] << 8 | (uint)*(byte *)*piVar12;
                piVar7[8] = piVar7[8] + 8;
                *piVar12 = *piVar12 + 1;
                *(int *)(*piVar7 + 4) = *(int *)(*piVar7 + 4) + -1;
                *(int *)(*piVar7 + 8) = *(int *)(*piVar7 + 8) + 1;
                if (*(int *)(*piVar7 + 8) == 0) {
                  piVar12 = (int *)(*piVar7 + 0xc);
                  *piVar12 = *piVar12 + 1;
                }
              }
              iVar13 = piVar7[8];
              piVar7[8] = iVar13 - local_c;
              local_1c = (uint)piVar7[7] >> ((byte)(iVar13 - local_c) & 0x1f) &
                         (1 << ((byte)local_c & 0x1f)) - 1U;
              while (iVar13 = local_48, local_c < 0x15) {
                if ((int)local_1c <= local_38[local_c]) {
                  iVar10 = local_1c - local_3c[local_c];
                  goto LAB_00428522;
                }
                local_c = local_c + 1;
switchD_00427597_caseD_25:
                piVar7[1] = 0x25;
                while (piVar7[8] < 1) {
                  piVar12 = (int *)*piVar7;
                  if (piVar12[1] == 0) goto LAB_00428c4d;
                  piVar7[7] = piVar7[7] << 8 | (uint)*(byte *)*piVar12;
                  piVar7[8] = piVar7[8] + 8;
                  *piVar12 = *piVar12 + 1;
                  *(int *)(*piVar7 + 4) = *(int *)(*piVar7 + 4) + -1;
                  *(int *)(*piVar7 + 8) = *(int *)(*piVar7 + 8) + 1;
                  if (*(int *)(*piVar7 + 8) == 0) {
                    piVar12 = (int *)(*piVar7 + 0xc);
                    *piVar12 = *piVar12 + 1;
                  }
                }
                local_58 = (uint)piVar7[7] >> ((char)piVar7[8] - 1U & 0x1f) & 1;
                local_1c = local_1c * 2 | local_58;
                piVar7[8] = piVar7[8] + -1;
              }
            }
          }
        }
      }
    }
    break;
  case 0x16:
    goto switchD_00427597_caseD_16;
  case 0x17:
    goto switchD_00427597_caseD_17;
  case 0x18:
    goto switchD_00427597_caseD_18;
  case 0x19:
    goto switchD_00427597_caseD_19;
  case 0x1a:
    goto switchD_00427597_caseD_1a;
  case 0x1b:
    goto switchD_00427597_caseD_1b;
  case 0x1c:
    goto switchD_00427597_caseD_1c;
  case 0x1d:
    goto switchD_00427597_caseD_1d;
  case 0x1e:
    goto switchD_00427597_caseD_1e;
  case 0x1f:
    goto switchD_00427597_caseD_1f;
  case 0x20:
    goto switchD_00427597_caseD_20;
  case 0x21:
    goto switchD_00427597_caseD_21;
  case 0x22:
    goto switchD_00427597_caseD_22;
  case 0x23:
    goto switchD_00427597_caseD_23;
  case 0x24:
    goto switchD_00427597_caseD_24;
  case 0x25:
    goto switchD_00427597_caseD_25;
  case 0x26:
    goto switchD_00427597_caseD_26;
  case 0x27:
    goto switchD_00427597_caseD_27;
  case 0x28:
    goto switchD_00427597_caseD_28;
  case 0x29:
    goto switchD_00427597_caseD_29;
  case 0x2b:
    goto switchD_00427597_caseD_2b;
  case 0x2c:
    goto switchD_00427597_caseD_2c;
  case 0x2d:
    goto switchD_00427597_caseD_2d;
  case 0x2e:
    goto switchD_00427597_caseD_2e;
  case 0x2f:
    goto switchD_00427597_caseD_2f;
  case 0x30:
    goto switchD_00427597_caseD_30;
  case 0x31:
    goto switchD_00427597_caseD_31;
  case 0x32:
    goto switchD_00427597_caseD_32;
  default:
    goto switchD_00427597_default;
  }
LAB_00428f47:
  local_48 = iVar13;
  uVar8 = 0xfffffffc;
switchD_00427597_default:
  piVar7[0x3e85] = local_8;
  piVar7[0x3e86] = local_18;
  piVar7[0x3e87] = local_28;
  piVar7[0x3e88] = local_44;
  piVar7[0x3e89] = local_2c;
  piVar7[0x3e8a] = local_34;
  piVar7[0x3e8b] = local_60;
  piVar7[0x3e8c] = local_48;
  piVar7[0x3e8d] = local_20;
  piVar7[0x3e8e] = local_30;
  piVar7[0x3e8f] = (int)local_54;
  piVar7[0x3e90] = local_14;
  piVar7[0x3e91] = local_10;
  piVar7[0x3e92] = local_4c;
  piVar7[0x3e93] = local_24;
  piVar7[0x3e94] = iVar5;
  piVar7[0x3e95] = local_c;
  piVar7[0x3e96] = local_1c;
  piVar7[0x3e97] = local_58;
  piVar7[0x3e98] = local_5c;
  piVar7[0x3e99] = local_50;
  piVar7[0x3e9a] = (int)local_38;
  piVar7[0x3e9b] = (int)local_3c;
  piVar7[0x3e9c] = (int)local_40;
  return uVar8;
LAB_00428522:
  iVar13 = local_48;
  if ((iVar10 < 0) || (0x101 < iVar10)) goto LAB_00428f47;
  local_30 = local_40[iVar10];
LAB_0042853c:
  iVar13 = local_48;
  if (local_30 == local_60) {
    if ((-1 < piVar7[0xd]) && (piVar7[0xd] < local_14)) {
      piVar7[3] = 0;
      *(undefined1 *)(piVar7 + 2) = 0;
      piVar7[0x318] = -1;
      piVar7[0x111] = 0;
      piVar12 = piVar7 + 0x112;
      piVar7[1] = 2;
      iVar13 = 0x100;
      piVar17 = piVar12;
      do {
        *piVar17 = piVar17[-0x102];
        piVar17 = piVar17 + 1;
        iVar13 = iVar13 + -1;
      } while (iVar13 != 0);
      iVar13 = 0x100;
      do {
        *piVar12 = *piVar12 + piVar12[-1];
        piVar12 = piVar12 + 1;
        iVar13 = iVar13 + -1;
      } while (iVar13 != 0);
      if ((char)piVar7[10] == '\0') {
        uVar15 = 0;
        local_8 = 0;
        if (0 < local_14) {
          do {
            uVar20 = (uint)*(byte *)(piVar7[0x313] + uVar15 * 4);
            puVar2 = (uint *)(piVar7[0x313] + piVar7[uVar20 + 0x111] * 4);
            *puVar2 = *puVar2 | uVar15 << 8;
            piVar7[uVar20 + 0x111] = piVar7[uVar20 + 0x111] + 1;
            uVar15 = uVar15 + 1;
            local_8 = uVar15;
          } while ((int)uVar15 < local_14);
        }
        iVar13 = piVar7[0x313];
        uVar15 = *(uint *)(iVar13 + piVar7[0xd] * 4);
        piVar7[0x110] = 0;
        uVar15 = uVar15 >> 8;
        piVar7[0xe] = uVar15;
        if ((char)piVar7[4] == '\0') {
          uVar15 = *(uint *)(iVar13 + piVar7[0xe] * 4);
          piVar7[0x110] = 1;
          piVar7[0xe] = uVar15;
          piVar7[0xe] = (uint)piVar7[0xe] >> 8;
          piVar7[0xf] = uVar15 & 0xff;
        }
        else {
          piVar7[5] = 0;
          piVar7[6] = 0;
          uVar15 = *(uint *)(iVar13 + uVar15 * 4);
          piVar7[0xe] = uVar15;
          piVar7[0xe] = (uint)piVar7[0xe] >> 8;
          piVar7[0xf] = uVar15 & 0xff;
          piVar7[0x110] = 1;
          piVar7[5] = DAT_004549b4;
          piVar7[5] = piVar7[5] + -1;
          piVar7[6] = 1;
          piVar7[0xf] = piVar7[0xf] ^ (uint)(piVar7[5] == 1);
        }
      }
      else {
        piVar12 = piVar7 + 0x212;
        iVar13 = 0x101;
        do {
          *piVar12 = piVar12[-0x101];
          piVar12 = piVar12 + 1;
          iVar13 = iVar13 + -1;
        } while (iVar13 != 0);
        uVar15 = 0;
        if (0 < local_14) {
          do {
            uVar20 = (uint)*(byte *)(piVar7[0x314] + uVar15 * 2);
            piVar12 = piVar7 + uVar20 + 0x212;
            *(short *)(piVar7[0x314] + uVar15 * 2) = (short)piVar7[uVar20 + 0x212];
            if ((uVar15 & 1) == 0) {
              pbVar22 = (byte *)(piVar7[0x315] + ((int)uVar15 >> 1));
              *pbVar22 = (byte)((uint)*piVar12 >> 0x10) | *pbVar22 & 0xf0;
            }
            else {
              pbVar22 = (byte *)(piVar7[0x315] + ((int)uVar15 >> 1));
              bVar14 = (byte)(*piVar12 >> 0xc);
              *pbVar22 = (*pbVar22 ^ bVar14) & 0xf ^ bVar14;
            }
            *piVar12 = *piVar12 + 1;
            uVar15 = uVar15 + 1;
          } while ((int)uVar15 < local_14);
        }
        local_8 = piVar7[0xd];
        local_18 = (*(byte *)(((int)local_8 >> 1) + piVar7[0x315]) >> (((byte)local_8 & 1) << 2) &
                   0xf) << 0x10 | (uint)*(ushort *)(piVar7[0x314] + local_8 * 2);
        do {
          puVar1 = (ushort *)(piVar7[0x314] + local_18 * 2);
          iVar10 = (int)local_18 >> 1;
          uVar15 = (*(byte *)(iVar10 + piVar7[0x315]) >> ((char)(local_18 & 1) << 2) & 0xf) << 0x10
                   | (uint)*puVar1;
          *puVar1 = (ushort)local_8;
          iVar13 = piVar7[0x315];
          if ((local_18 & 1) == 0) {
            *(byte *)(iVar10 + iVar13) = (byte)(local_8 >> 0x10) | *(byte *)(iVar10 + iVar13) & 0xf0
            ;
          }
          else {
            bVar14 = (byte)((int)local_8 >> 0xc);
            *(byte *)(iVar10 + iVar13) = (*(byte *)(iVar10 + iVar13) ^ bVar14) & 0xf ^ bVar14;
          }
          bVar23 = local_18 != piVar7[0xd];
          local_8 = local_18;
          local_18 = uVar15;
        } while (bVar23);
        iVar13 = piVar7[0xd];
        piVar7[0xe] = iVar13;
        piVar7[0x110] = 0;
        if ((char)piVar7[4] == '\0') {
          iVar13 = FUN_004255df(iVar13,(int)(piVar7 + 0x111));
          piVar7[0xf] = iVar13;
          uVar15 = piVar7[0xe];
          bVar14 = *(byte *)((uVar15 >> 1) + piVar7[0x315]);
          uVar4 = *(ushort *)(piVar7[0x314] + uVar15 * 2);
          piVar7[0x110] = piVar7[0x110] + 1;
          piVar7[0xe] = (bVar14 >> (((byte)uVar15 & 1) << 2) & 0xf) << 0x10 | (uint)uVar4;
        }
        else {
          piVar7[5] = 0;
          piVar7[6] = 0;
          uVar20 = FUN_004255df(iVar13,(int)(piVar7 + 0x111));
          uVar15 = piVar7[0xe];
          piVar7[0xf] = uVar20;
          bVar14 = *(byte *)((uVar15 >> 1) + piVar7[0x315]);
          uVar4 = *(ushort *)(piVar7[0x314] + uVar15 * 2);
          piVar7[0x110] = piVar7[0x110] + 1;
          piVar7[0xe] = (bVar14 >> (((byte)uVar15 & 1) << 2) & 0xf) << 0x10 | (uint)uVar4;
          if (piVar7[5] == 0) {
            iVar13 = piVar7[6] + 1;
            piVar7[5] = (&DAT_004549b4)[piVar7[6]];
            piVar7[6] = iVar13;
            if (iVar13 == 0x200) {
              piVar7[6] = 0;
            }
          }
          piVar7[5] = piVar7[5] + -1;
          piVar7[0xf] = piVar7[5] == 1 ^ uVar20;
        }
      }
      goto LAB_00428c4d;
    }
    goto LAB_00428f47;
  }
  if ((local_30 == 0) || (local_30 == 1)) goto LAB_004287e1;
  if ((int)local_54 <= local_14) goto LAB_00428f47;
  uVar15 = local_30 - 1;
  if (uVar15 < 0x10) {
    local_78[0] = piVar7[0x79f];
    bVar14 = *(byte *)(local_78[0] + uVar15 + 0xe7c + (int)piVar7);
    param_1 = (int *)((uint)bVar14 << 0x18);
    if (3 < uVar15) {
      iVar13 = (int)piVar7 + 0xe7b;
      puVar11 = (undefined1 *)(local_78[0] + uVar15 + iVar13);
      local_68 = (int)piVar7 + (0xe7c - iVar13);
      local_6c = (int)piVar7 + (0xe7a - iVar13);
      local_70 = (int)piVar7 + (0xe78 - iVar13);
      local_64 = (int)piVar7 + (0xe79 - iVar13);
      uVar20 = uVar15 >> 2;
      do {
        uVar15 = uVar15 - 4;
        puVar11[local_68] = *puVar11;
        *puVar11 = puVar11[local_6c];
        puVar11[local_6c] = puVar11[local_64];
        puVar11[local_64] = puVar11[local_70];
        puVar11 = puVar11 + -4;
        uVar20 = uVar20 - 1;
      } while (uVar20 != 0);
    }
    if (uVar15 != 0) {
      do {
        *(undefined1 *)((int)piVar7 + uVar15 + local_78[0] + 0xe7c) =
             *(undefined1 *)((int)piVar7 + (uVar15 - 1) + local_78[0] + 0xe7c);
        uVar15 = uVar15 - 1;
      } while (uVar15 != 0);
    }
    *(byte *)(local_78[0] + 0xe7c + (int)piVar7) = bVar14;
  }
  else {
    uVar20 = uVar15 >> 4;
    piVar12 = piVar7 + uVar20 + 0x79f;
    iVar13 = (uVar15 & 0xf) + piVar7[uVar20 + 0x79f];
    bVar14 = *(byte *)(iVar13 + 0xe7c + (int)piVar7);
    param_1 = (int *)((uint)bVar14 << 0x18);
    if (piVar7[uVar20 + 0x79f] < iVar13) {
      do {
        *(undefined1 *)(iVar13 + 0xe7c + (int)piVar7) =
             *(undefined1 *)(iVar13 + 0xe7b + (int)piVar7);
        iVar13 = iVar13 + -1;
      } while (*piVar12 < iVar13);
    }
    *piVar12 = *piVar12 + 1;
    for (; uVar20 != 0; uVar20 = uVar20 - 1) {
      *piVar12 = *piVar12 + -1;
      iVar13 = *piVar12;
      piVar17 = piVar12 + -1;
      piVar12 = piVar12 + -1;
      *(undefined1 *)(iVar13 + 0xe7c + (int)piVar7) =
           *(undefined1 *)((int)piVar7 + *piVar17 + 0xe8b);
    }
    piVar7[0x79f] = piVar7[0x79f] + -1;
    *(byte *)(piVar7[0x79f] + 0xe7c + (int)piVar7) = bVar14;
    if (piVar7[0x79f] == 0) {
      iVar10 = 0xfff;
      piVar12 = piVar7 + 0x7ae;
      iVar13 = 0x10;
      do {
        iVar21 = 0xf;
        do {
          iVar16 = iVar10;
          iVar19 = iVar21 + *piVar12;
          iVar10 = iVar16 + -1;
          iVar21 = iVar21 + -1;
          *(undefined1 *)(iVar16 + 0xe7c + (int)piVar7) =
               *(undefined1 *)(iVar19 + 0xe7c + (int)piVar7);
        } while (-1 < iVar21);
        *piVar12 = iVar16;
        piVar12 = piVar12 + -1;
        iVar13 = iVar13 + -1;
      } while (iVar13 != 0);
    }
  }
  pbVar22 = (byte *)(((uint)param_1 >> 0x18) + 0xd7c + (int)piVar7);
  piVar7[*(byte *)(((uint)param_1 >> 0x18) + 0xd7c + (int)piVar7) + 0x10] =
       piVar7[*(byte *)(((uint)param_1 >> 0x18) + 0xd7c + (int)piVar7) + 0x10] + 1;
  if ((char)piVar7[10] == '\0') {
    *(uint *)(piVar7[0x313] + local_14 * 4) = (uint)*pbVar22;
  }
  else {
    *(ushort *)(piVar7[0x314] + local_14 * 2) = (ushort)*pbVar22;
  }
  local_14 = local_14 + 1;
  if (local_20 == 0) {
    iVar13 = local_48 + 1;
    if ((int)local_34 <= iVar13) goto LAB_00428f47;
    local_5c = (uint)*(byte *)(local_48 + 0x1ebd + (int)piVar7);
    local_20 = 0x32;
    local_50 = piVar7[local_5c + 15999];
    local_38 = piVar7 + local_5c * 0x102 + 0x2c5b;
    local_40 = piVar7 + local_5c * 0x102 + 0x3873;
    local_3c = piVar7 + local_5c * 0x102 + 0x3267;
    local_48 = iVar13;
  }
  local_20 = local_20 + -1;
  local_c = local_50;
switchD_00427597_caseD_28:
  piVar7[1] = 0x28;
  while (piVar7[8] < local_c) {
    piVar12 = (int *)*piVar7;
    if (piVar12[1] == 0) goto LAB_00428c4d;
    piVar7[7] = piVar7[7] << 8 | (uint)*(byte *)*piVar12;
    piVar7[8] = piVar7[8] + 8;
    *piVar12 = *piVar12 + 1;
    *(int *)(*piVar7 + 4) = *(int *)(*piVar7 + 4) + -1;
    *(int *)(*piVar7 + 8) = *(int *)(*piVar7 + 8) + 1;
    if (*(int *)(*piVar7 + 8) == 0) {
      piVar12 = (int *)(*piVar7 + 0xc);
      *piVar12 = *piVar12 + 1;
    }
  }
  iVar13 = piVar7[8];
  piVar7[8] = iVar13 - local_c;
  local_1c = (uint)piVar7[7] >> ((byte)(iVar13 - local_c) & 0x1f) &
             (1 << ((byte)local_c & 0x1f)) - 1U;
  while( true ) {
    iVar13 = local_48;
    if (0x14 < local_c) goto LAB_00428f47;
    if ((int)local_1c <= local_38[local_c]) break;
    local_c = local_c + 1;
switchD_00427597_caseD_29:
    piVar7[1] = 0x29;
    while (piVar7[8] < 1) {
      piVar12 = (int *)*piVar7;
      if (piVar12[1] == 0) goto LAB_00428c4d;
      piVar7[7] = piVar7[7] << 8 | (uint)*(byte *)*piVar12;
      piVar7[8] = piVar7[8] + 8;
      *piVar12 = *piVar12 + 1;
      *(int *)(*piVar7 + 4) = *(int *)(*piVar7 + 4) + -1;
      *(int *)(*piVar7 + 8) = *(int *)(*piVar7 + 8) + 1;
      if (*(int *)(*piVar7 + 8) == 0) {
        piVar12 = (int *)(*piVar7 + 0xc);
        *piVar12 = *piVar12 + 1;
      }
    }
    local_58 = (uint)piVar7[7] >> ((char)piVar7[8] - 1U & 0x1f) & 1;
    local_1c = local_1c * 2 | local_58;
    piVar7[8] = piVar7[8] + -1;
  }
  iVar10 = local_1c - local_3c[local_c];
  goto LAB_00428522;
LAB_004287e1:
  local_10 = -1;
  local_4c = 1;
  do {
    if (local_30 == 0) {
      local_10 = local_10 + local_4c;
    }
    else if (local_30 == 1) {
      local_10 = local_10 + local_4c * 2;
    }
    local_4c = local_4c * 2;
    if (local_20 == 0) {
      iVar13 = local_48 + 1;
      if ((int)local_34 <= iVar13) goto LAB_00428f47;
      local_5c = (uint)*(byte *)(local_48 + 0x1ebd + (int)piVar7);
      local_20 = 0x32;
      local_50 = piVar7[local_5c + 15999];
      local_38 = piVar7 + local_5c * 0x102 + 0x2c5b;
      local_40 = piVar7 + local_5c * 0x102 + 0x3873;
      local_3c = piVar7 + local_5c * 0x102 + 0x3267;
      local_48 = iVar13;
    }
    local_20 = local_20 + -1;
    local_c = local_50;
switchD_00427597_caseD_26:
    piVar7[1] = 0x26;
    while (piVar7[8] < local_c) {
      piVar12 = (int *)*piVar7;
      if (piVar12[1] == 0) goto LAB_00428c4d;
      piVar7[7] = piVar7[7] << 8 | (uint)*(byte *)*piVar12;
      piVar7[8] = piVar7[8] + 8;
      *piVar12 = *piVar12 + 1;
      *(int *)(*piVar7 + 4) = *(int *)(*piVar7 + 4) + -1;
      *(int *)(*piVar7 + 8) = *(int *)(*piVar7 + 8) + 1;
      if (*(int *)(*piVar7 + 8) == 0) {
        piVar12 = (int *)(*piVar7 + 0xc);
        *piVar12 = *piVar12 + 1;
      }
    }
    iVar13 = piVar7[8];
    piVar7[8] = iVar13 - local_c;
    local_1c = (uint)piVar7[7] >> ((byte)(iVar13 - local_c) & 0x1f) &
               (1 << ((byte)local_c & 0x1f)) - 1U;
    while( true ) {
      iVar13 = local_48;
      if (0x14 < local_c) goto LAB_00428f47;
      if ((int)local_1c <= local_38[local_c]) break;
      local_c = local_c + 1;
switchD_00427597_caseD_27:
      piVar7[1] = 0x27;
      while (piVar7[8] < 1) {
        piVar12 = (int *)*piVar7;
        if (piVar12[1] == 0) goto LAB_00428c4d;
        piVar7[7] = piVar7[7] << 8 | (uint)*(byte *)*piVar12;
        piVar7[8] = piVar7[8] + 8;
        *piVar12 = *piVar12 + 1;
        *(int *)(*piVar7 + 4) = *(int *)(*piVar7 + 4) + -1;
        *(int *)(*piVar7 + 8) = *(int *)(*piVar7 + 8) + 1;
        if (*(int *)(*piVar7 + 8) == 0) {
          piVar12 = (int *)(*piVar7 + 0xc);
          *piVar12 = *piVar12 + 1;
        }
      }
      local_58 = (uint)piVar7[7] >> ((char)piVar7[8] - 1U & 0x1f) & 1;
      local_1c = local_1c * 2 | local_58;
      piVar7[8] = piVar7[8] + -1;
    }
    iVar10 = local_1c - local_3c[local_c];
    if ((iVar10 < 0) || (0x101 < iVar10)) goto LAB_00428f47;
    local_30 = local_40[iVar10];
  } while ((local_30 == 0) || (local_30 == 1));
  local_10 = local_10 + 1;
  bVar14 = *(byte *)(*(byte *)(piVar7[0x79f] + 0xe7c + (int)piVar7) + 0xd7c + (int)piVar7);
  piVar7[bVar14 + 0x10] = piVar7[bVar14 + 0x10] + local_10;
  if ((char)piVar7[10] == '\0') {
    for (; 0 < local_10; local_10 = local_10 + -1) {
      if ((int)local_54 <= local_14) goto LAB_00428f47;
      *(uint *)(piVar7[0x313] + local_14 * 4) = (uint)bVar14;
      local_14 = local_14 + 1;
    }
  }
  else {
    for (; 0 < local_10; local_10 = local_10 + -1) {
      if ((int)local_54 <= local_14) goto LAB_00428f47;
      *(ushort *)(piVar7[0x314] + local_14 * 2) = (ushort)bVar14;
      local_14 = local_14 + 1;
    }
  }
  goto LAB_0042853c;
switchD_00427597_caseD_30:
  param_1[1] = 0x30;
  while (param_1[8] < 8) {
    piVar12 = (int *)*param_1;
    if (piVar12[1] == 0) goto LAB_00428c4d;
    param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
    param_1[8] = param_1[8] + 8;
    *piVar12 = *piVar12 + 1;
    *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
    *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
    if (*(int *)(*param_1 + 8) == 0) {
      piVar12 = (int *)(*param_1 + 0xc);
      *piVar12 = *piVar12 + 1;
    }
  }
  iVar13 = param_1[8];
  param_1[8] = iVar13 + -8;
  param_1[0x317] = param_1[0x317] << 8 | (uint)param_1[7] >> ((char)iVar13 - 8U & 0x1f) & 0xff;
switchD_00427597_caseD_31:
  param_1[1] = 0x31;
  while (param_1[8] < 8) {
    piVar12 = (int *)*param_1;
    if (piVar12[1] == 0) goto LAB_00428c4d;
    param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
    param_1[8] = param_1[8] + 8;
    *piVar12 = *piVar12 + 1;
    *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
    *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
    if (*(int *)(*param_1 + 8) == 0) {
      piVar12 = (int *)(*param_1 + 0xc);
      *piVar12 = *piVar12 + 1;
    }
  }
  iVar13 = param_1[8];
  param_1[8] = iVar13 + -8;
  param_1[0x317] = param_1[0x317] << 8 | (uint)param_1[7] >> ((char)iVar13 - 8U & 0x1f) & 0xff;
switchD_00427597_caseD_32:
  param_1[1] = 0x32;
  while (param_1[8] < 8) {
    piVar12 = (int *)*param_1;
    if (piVar12[1] == 0) goto LAB_00428c4d;
    param_1[7] = param_1[7] << 8 | (uint)*(byte *)*piVar12;
    param_1[8] = param_1[8] + 8;
    *piVar12 = *piVar12 + 1;
    *(int *)(*param_1 + 4) = *(int *)(*param_1 + 4) + -1;
    *(int *)(*param_1 + 8) = *(int *)(*param_1 + 8) + 1;
    if (*(int *)(*param_1 + 8) == 0) {
      piVar12 = (int *)(*param_1 + 0xc);
      *piVar12 = *piVar12 + 1;
    }
  }
  iVar13 = param_1[8];
  param_1[1] = 1;
  uVar8 = 4;
  param_1[8] = iVar13 + -8;
  param_1[0x317] = param_1[0x317] << 8 | (uint)param_1[7] >> ((char)iVar13 - 8U & 0x1f) & 0xff;
  goto switchD_00427597_default;
LAB_00428c4d:
  uVar8 = 0;
  goto switchD_00427597_default;
}

