* 評価値テーブルは先手用しかないので、後手番の指し手を先手番に１８０°回転するように修正
* FIXME v_a53_0, v_a54_0, v_a55_0 の学習部は壊れてる？ v_a52_0 をしばらく floodgate へ放流することに
* TODO weaken, strengthen でも ranking_resolution を使いたい
* TODO 好手が稀で、好手０、悪手全部になってしまう。悪手の下げ幅を少し、好手の上げ幅を多めにしてはどうか？
  * 例えば議員総数の５分の１を単位として、３単位上げるとか、１単位下げるとか
* TODO 票の５割で好手／悪手を分けているのがダメなのでは？　１割でも好手では？　好手が少なすぎるから
