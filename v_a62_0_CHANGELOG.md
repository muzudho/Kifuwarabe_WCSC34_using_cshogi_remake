* v_a60_0 と v_a61_0 の間, v_a61_0 と v_a62_0 で、評価値テーブルの仕様を変更しました。互換性はありません
* 指し手K は、先手視点に加え、さらに右辺のみ使用という条件を付けました
* TODO 評価値テーブルも左辺を削除したい
* FIXME ３手詰めで、１手目は合っていて３手目を間違えたとき、減点すべきは３手目では？
  * 何手目まで合っているという判断をどうやってするか？