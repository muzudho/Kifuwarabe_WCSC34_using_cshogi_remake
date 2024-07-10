# Kifuwarabe_WCSC34_using_cshogi_remake

WCSC34 のきふわらべの作り直し


# 動作テスト

```shell
# 将棋エンジンを起動直後
selfmatch
```


# 仕様（Specification）

v_a53_0 版から、 `src_sq` は `srcsq` に改名し、値は 0～80 の整数または None とする。  
0～80 は、縦型の盤上のマスを指す。  

`src_drop` は `srcdrop` に改名し、0～80 を欠番とし、  
81 は飛打、 82 は角打、 83 は金打、 84 は銀打、 85 は桂打、 86 は香打、 87は歩打とする。  

また、上記２つを兼ねた `srcloc` を追加する。値は 0～87 とする。  
