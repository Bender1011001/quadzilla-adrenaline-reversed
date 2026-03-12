// FUN_0041d527 @ 0041d527


int __cdecl FUN_0041d527(int *param_1,byte *param_2,undefined4 *param_3)

{
  int iVar1;
  uint uVar2;
  WCHAR *pWVar3;
  undefined4 uVar4;
  short *psVar5;
  int *piVar6;
  LPSTR pCVar7;
  byte bVar8;
  int iVar9;
  WCHAR *pWVar10;
  LPSTR pCVar11;
  undefined8 uVar12;
  WCHAR local_250 [255];
  undefined1 local_51;
  undefined4 local_50;
  undefined4 local_4c;
  CHAR local_48 [4];
  undefined4 local_44;
  int local_40;
  int local_3c;
  int local_38;
  WCHAR *local_34;
  int local_30;
  int local_2c;
  int local_28;
  undefined8 local_24;
  char local_1a;
  char local_19;
  int local_18;
  LPSTR local_14;
  WCHAR *local_10;
  int local_c;
  uint local_8;
  
  local_40 = 0;
  local_14 = (LPSTR)0x0;
  bVar8 = *param_2;
  param_2 = param_2 + 1;
  local_18 = 0;
  local_34 = (WCHAR *)0x0;
  do {
    if ((bVar8 == 0) || (local_18 < 0)) {
      return local_18;
    }
    if (((char)bVar8 < ' ') || ('x' < (char)bVar8)) {
      uVar2 = 0;
    }
    else {
      uVar2 = (byte)"GAIsProcessorFeaturePresent"[(char)bVar8 + 0x12] & 0xf;
    }
    local_40 = (int)(char)(&DAT_0043d7f8)[uVar2 * 8 + local_40] >> 4;
    switch(local_40) {
    case 0:
switchD_0041d5a3_caseD_0:
      local_30 = 0;
      if ((PTR_DAT_00451010[(uint)bVar8 * 2 + 1] & 0x80) != 0) {
        FUN_0041dcc5((int)(char)bVar8,param_1,&local_18);
        bVar8 = *param_2;
        param_2 = param_2 + 1;
      }
      FUN_0041dcc5((int)(char)bVar8,param_1,&local_18);
      break;
    case 1:
      local_c = -1;
      local_44 = 0;
      local_3c = 0;
      local_2c = 0;
      local_28 = 0;
      local_8 = 0;
      local_30 = 0;
      break;
    case 2:
      if (bVar8 == 0x20) {
        local_8 = local_8 | 2;
      }
      else if (bVar8 == 0x23) {
        local_8 = local_8 | 0x80;
      }
      else if (bVar8 == 0x2b) {
        local_8 = local_8 | 1;
      }
      else if (bVar8 == 0x2d) {
        local_8 = local_8 | 4;
      }
      else if (bVar8 == 0x30) {
        local_8 = local_8 | 8;
      }
      break;
    case 3:
      if (bVar8 == 0x2a) {
        local_2c = FUN_0041dd63((int *)&param_3);
        if (local_2c < 0) {
          local_8 = local_8 | 4;
          local_2c = -local_2c;
        }
      }
      else {
        local_2c = (char)bVar8 + -0x30 + local_2c * 10;
      }
      break;
    case 4:
      local_c = 0;
      break;
    case 5:
      if (bVar8 == 0x2a) {
        local_c = FUN_0041dd63((int *)&param_3);
        if (local_c < 0) {
          local_c = -1;
        }
      }
      else {
        local_c = (char)bVar8 + -0x30 + local_c * 10;
      }
      break;
    case 6:
      if (bVar8 == 0x49) {
        if ((*param_2 != 0x36) || (param_2[1] != 0x34)) {
          local_40 = 0;
          goto switchD_0041d5a3_caseD_0;
        }
        param_2 = param_2 + 2;
        local_8 = local_8 | 0x8000;
      }
      else if (bVar8 == 0x68) {
        local_8 = local_8 | 0x20;
      }
      else if (bVar8 == 0x6c) {
        local_8 = local_8 | 0x10;
      }
      else if (bVar8 == 0x77) {
        local_8 = local_8 | 0x800;
      }
      break;
    case 7:
      pWVar10 = local_10;
      if ((char)bVar8 < 'h') {
        if ((char)bVar8 < 'e') {
          if ((char)bVar8 < 'Y') {
            if (bVar8 != 0x58) {
              if (bVar8 == 0x43) {
                if ((local_8 & 0x830) == 0) {
                  local_8 = local_8 | 0x800;
                }
                goto LAB_0041d7f8;
              }
              if ((bVar8 != 0x45) && (bVar8 != 0x47)) {
                if (bVar8 == 0x53) {
                  if ((local_8 & 0x830) == 0) {
                    local_8 = local_8 | 0x800;
                  }
                  goto LAB_0041d768;
                }
                goto LAB_0041db7b;
              }
              local_44 = 1;
              bVar8 = bVar8 + 0x20;
              goto LAB_0041d7ca;
            }
LAB_0041d9d7:
            local_38 = 7;
LAB_0041d9de:
            local_14 = (LPSTR)0x10;
            if ((local_8 & 0x80) != 0) {
              local_1a = '0';
              local_19 = (char)local_38 + 'Q';
              local_28 = 2;
            }
            goto LAB_0041da47;
          }
          if (bVar8 == 0x5a) {
            psVar5 = (short *)FUN_0041dd63((int *)&param_3);
            if ((psVar5 == (short *)0x0) ||
               (pWVar10 = *(WCHAR **)(psVar5 + 2), pWVar10 == (WCHAR *)0x0)) {
              local_10 = (WCHAR *)PTR_DAT_00450ed0;
              pWVar10 = (WCHAR *)PTR_DAT_00450ed0;
              goto LAB_0041d958;
            }
            if ((local_8 & 0x800) == 0) {
              local_30 = 0;
              local_14 = (LPSTR)(int)*psVar5;
            }
            else {
              local_30 = 1;
              local_14 = (LPSTR)((uint)(int)*psVar5 >> 1);
            }
          }
          else if (bVar8 == 99) {
LAB_0041d7f8:
            if ((local_8 & 0x810) == 0) {
              uVar4 = FUN_0041dd63((int *)&param_3);
              local_250[0]._0_1_ = (undefined1)uVar4;
              local_14 = (LPSTR)0x1;
            }
            else {
              uVar4 = FUN_0041dd80((int *)&param_3);
              local_14 = FUN_00421b44((LPSTR)local_250,(WCHAR)uVar4);
              if ((int)local_14 < 0) {
                local_3c = 1;
              }
            }
            pWVar10 = local_250;
          }
          else if (bVar8 == 100) goto LAB_0041da3c;
        }
        else {
LAB_0041d7ca:
          local_8 = local_8 | 0x40;
          pWVar10 = local_250;
          pWVar3 = local_250;
          if (local_c < 0) {
            local_c = 6;
          }
          else if (local_c == 0) {
            if (bVar8 == 0x67) {
              local_c = 1;
            }
          }
          else {
            if (0x200 < local_c) {
              local_c = 0x200;
            }
            if ((0xa3 < local_c) &&
               (local_10 = local_250, local_34 = (WCHAR *)_malloc(local_c + 0x15d),
               pWVar10 = local_34, pWVar3 = local_34, local_34 == (WCHAR *)0x0)) {
              local_c = 0xa3;
              pWVar10 = local_250;
              pWVar3 = local_10;
            }
          }
          local_10 = pWVar3;
          local_50 = *param_3;
          local_4c = param_3[1];
          param_3 = param_3 + 2;
          (*(code *)PTR_FUN_00450eb8)(&local_50,pWVar10,(int)(char)bVar8,local_c,local_44);
          uVar2 = local_8 & 0x80;
          if ((uVar2 != 0) && (local_c == 0)) {
            (*(code *)PTR_FUN_00450ec4)(pWVar10);
          }
          if ((bVar8 == 0x67) && (uVar2 == 0)) {
            (*(code *)PTR_FUN_00450ebc)(pWVar10);
          }
          if ((char)*pWVar10 == '-') {
            local_8 = local_8 | 0x100;
            pWVar10 = (WCHAR *)((int)pWVar10 + 1);
            local_10 = pWVar10;
          }
LAB_0041d958:
          local_14 = (LPSTR)_strlen((char *)pWVar10);
          pWVar10 = local_10;
        }
LAB_0041db7b:
        local_10 = pWVar10;
        uVar2 = local_8;
        if (local_3c == 0) {
          if ((local_8 & 0x40) != 0) {
            if ((local_8 & 0x100) == 0) {
              if ((local_8 & 1) == 0) {
                if ((local_8 & 2) == 0) goto LAB_0041dbb3;
                local_1a = ' ';
              }
              else {
                local_1a = '+';
              }
            }
            else {
              local_1a = '-';
            }
            local_28 = 1;
          }
LAB_0041dbb3:
          iVar9 = (local_2c - local_28) - (int)local_14;
          if ((local_8 & 0xc) == 0) {
            FUN_0041dcfa(0x20,iVar9,param_1,&local_18);
          }
          FUN_0041dd2b(&local_1a,local_28,param_1,&local_18);
          if (((uVar2 & 8) != 0) && ((uVar2 & 4) == 0)) {
            FUN_0041dcfa(0x30,iVar9,param_1,&local_18);
          }
          if ((local_30 == 0) || (pCVar11 = local_14, pWVar10 = local_10, (int)local_14 < 1)) {
            FUN_0041dd2b((char *)local_10,(int)local_14,param_1,&local_18);
          }
          else {
            do {
              pCVar11 = pCVar11 + -1;
              pCVar7 = FUN_00421b44(local_48,*pWVar10);
              if ((int)pCVar7 < 1) break;
              FUN_0041dd2b(local_48,(int)pCVar7,param_1,&local_18);
              pWVar10 = pWVar10 + 1;
            } while (pCVar11 != (LPSTR)0x0);
          }
          if ((local_8 & 4) != 0) {
            FUN_0041dcfa(0x20,iVar9,param_1,&local_18);
          }
        }
      }
      else {
        if (bVar8 == 0x69) {
LAB_0041da3c:
          local_8 = local_8 | 0x40;
LAB_0041da40:
          local_14 = (LPSTR)0xa;
LAB_0041da47:
          if ((local_8 & 0x8000) == 0) {
            if ((local_8 & 0x20) == 0) {
              if ((local_8 & 0x40) == 0) {
                uVar2 = FUN_0041dd63((int *)&param_3);
                local_24 = (ulonglong)uVar2;
                goto LAB_0041da9a;
              }
              uVar2 = FUN_0041dd63((int *)&param_3);
            }
            else if ((local_8 & 0x40) == 0) {
              uVar2 = FUN_0041dd63((int *)&param_3);
              uVar2 = uVar2 & 0xffff;
            }
            else {
              uVar4 = FUN_0041dd63((int *)&param_3);
              uVar2 = (uint)(short)uVar4;
            }
            local_24 = (ulonglong)(int)uVar2;
          }
          else {
            local_24 = FUN_0041dd70((int *)&param_3);
          }
LAB_0041da9a:
          iVar9 = (int)(local_24 >> 0x20);
          if ((((local_8 & 0x40) != 0) && (iVar9 == 0 || (longlong)local_24 < 0)) &&
             ((longlong)local_24 < 0)) {
            local_8 = local_8 | 0x100;
            local_24 = CONCAT44(-(iVar9 + (uint)((int)local_24 != 0)),-(int)local_24);
          }
          if ((local_8 & 0x8000) == 0) {
            local_24 = local_24 & 0xffffffff;
          }
          if (local_c < 0) {
            local_c = 1;
          }
          else {
            local_8 = local_8 & 0xfffffff7;
            if (0x200 < local_c) {
              local_c = 0x200;
            }
          }
          if ((uint)local_24 == 0 && local_24._4_4_ == 0) {
            local_28 = 0;
          }
          local_10 = (WCHAR *)&local_51;
          while( true ) {
            pCVar11 = local_14;
            iVar9 = local_c + -1;
            if ((local_c < 1) && ((uint)local_24 == 0 && local_24._4_4_ == 0)) break;
            uVar2 = (int)local_14 >> 0x1f;
            local_c = iVar9;
            uVar12 = __aullrem((uint)local_24,local_24._4_4_,(uint)local_14,uVar2);
            iVar9 = (int)uVar12 + 0x30;
            local_24 = __aulldiv((uint)local_24,local_24._4_4_,(uint)pCVar11,uVar2);
            if (0x39 < iVar9) {
              iVar9 = iVar9 + local_38;
            }
            pWVar10 = (WCHAR *)((int)local_10 + -1);
            *(char *)local_10 = (char)iVar9;
            local_10 = pWVar10;
          }
          iVar1 = -(int)local_10;
          local_14 = &local_51 + iVar1;
          pWVar10 = (WCHAR *)((int)local_10 + 1);
          local_c = iVar9;
          if (((local_8 & 0x200) != 0) && ((*(char *)pWVar10 != '0' || (local_14 == (LPSTR)0x0)))) {
            *(char *)local_10 = '0';
            local_14 = (LPSTR)((int)&local_50 + iVar1);
            pWVar10 = local_10;
          }
          goto LAB_0041db7b;
        }
        if (bVar8 != 0x6e) {
          if (bVar8 == 0x6f) {
            local_14 = (LPSTR)0x8;
            if ((local_8 & 0x80) != 0) {
              local_8 = local_8 | 0x200;
            }
            goto LAB_0041da47;
          }
          if (bVar8 == 0x70) {
            local_c = 8;
            goto LAB_0041d9d7;
          }
          if (bVar8 == 0x73) {
LAB_0041d768:
            iVar9 = 0x7fffffff;
            if (local_c != -1) {
              iVar9 = local_c;
            }
            pWVar3 = (WCHAR *)FUN_0041dd63((int *)&param_3);
            if ((local_8 & 0x810) == 0) {
              pWVar10 = pWVar3;
              if (pWVar3 == (WCHAR *)0x0) {
                pWVar3 = (WCHAR *)PTR_DAT_00450ed0;
                pWVar10 = (WCHAR *)PTR_DAT_00450ed0;
              }
              for (; (iVar9 != 0 && ((char)*pWVar3 != '\0')); pWVar3 = (WCHAR *)((int)pWVar3 + 1)) {
                iVar9 = iVar9 + -1;
              }
              local_14 = (LPSTR)((int)pWVar3 - (int)pWVar10);
            }
            else {
              if (pWVar3 == (WCHAR *)0x0) {
                pWVar3 = (WCHAR *)PTR_DAT_00450ed4;
              }
              local_30 = 1;
              for (pWVar10 = pWVar3; (iVar9 != 0 && (*pWVar10 != L'\0')); pWVar10 = pWVar10 + 1) {
                iVar9 = iVar9 + -1;
              }
              local_14 = (LPSTR)((int)pWVar10 - (int)pWVar3 >> 1);
              pWVar10 = pWVar3;
            }
            goto LAB_0041db7b;
          }
          if (bVar8 != 0x75) {
            if (bVar8 != 0x78) goto LAB_0041db7b;
            local_38 = 0x27;
            goto LAB_0041d9de;
          }
          goto LAB_0041da40;
        }
        piVar6 = (int *)FUN_0041dd63((int *)&param_3);
        if ((local_8 & 0x20) == 0) {
          *piVar6 = local_18;
        }
        else {
          *(undefined2 *)piVar6 = (undefined2)local_18;
        }
        local_3c = 1;
      }
      if (local_34 != (WCHAR *)0x0) {
        FUN_0041c6b8((undefined *)local_34);
        local_34 = (WCHAR *)0x0;
      }
    }
    bVar8 = *param_2;
    param_2 = param_2 + 1;
  } while( true );
}

