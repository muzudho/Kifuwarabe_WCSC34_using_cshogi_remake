* '2i3a', '3i4a' という指し手を生成する原因を探し、再発しないように修正したい
  * promote=False にハードコーディングされていて成りの手が成らずの手になって後手が９段目まで歩を突いていたのが原因だった
* TODO weaken, strengthen を修正したい
    * FIXME strengthen すると ‰が 2500 になるのおかしい
* テスト局面： position sfen lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1 moves 2g2f 5a6b 2f2e 3a3b 2e2d 6b5b 2d2c+ 5b5a 2c2b 5a4b 2b3b 4b5b 3b4a 9c9d 2h2b+ 5b4a G*3a 4a5a 2b2a 5a6b 2a3b 6b5a B*4b 8b4b 3b3c 5a6b 3c4b B*5b N*5d 5c5d S*5c 6b7b 5c5b+ 7b8b 5b6a N*5b 4b5b 7a6b 5b6b 8b9c B*7a 9c8d N*7f 8d8e G*8f 8e7d R*7e
* 行き場のない場所に歩を進めるコマンド： position sfen lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1 moves 2g2f 5a6b 2f2e 3a3b 2e2d 6b5b 2d2c+ 5b5a 2c2b 5a4b 2b3b 4b5b 3b4a 9c9d 2h2b+ 5b4a G*3a 4a5a 2b2a 5a6b 2a3b 6b5a B*4b 8b4b 3b3c 5a6b 3c4b B*5b N*5d 5c5d S*5c 6b7b 5c5b+ 7b8b 5b6a N*5b 4b5b 7a6b 5b6b 8b9c B*7a 9c8d N*7f 8d8e G*7b P*3h 5i5h 3h3i
