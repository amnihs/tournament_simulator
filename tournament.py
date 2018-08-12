import random
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
pd.set_option("display.max_rows", 101)

# name, score, given_point, entry_round,rate
kohshien_df = pd.read_csv('tournament.csv', encoding="shift-jis")

def attack_rank(point):
    score, given_point, rate = point
    score = score * rate
    if score >= 12:
        return 'SS'
    elif score >= 10:
        return 'S'
    elif score >= 8:
        return 'A'
    elif score >= 6:
        return 'B'
    elif score >= 4:
        return 'C'
    else:
        return 'D'

def defence_rank(point):
    score, given_point, rate = point
    given_point = given_point / rate
    if given_point < 0.6:
        return 'SS'
    elif given_point < 1.2:
        return 'S'
    elif given_point < 1.8:
        return 'A'
    elif given_point < 2.4:
        return 'B'
    elif given_point < 3:
        return 'C'
    else:
        return 'D'
    
def winning_deviation(winning_count):
    deviation = (winning_count - mean) / std
    deviation_value = 50 + (deviation * 10)
    return deviation_value

def add_rate(calc_deviation):
    return (calc_deviation + 50) / 100

# 偏差値計算用
mean = np.mean(kohshien_df['winning_count'])
std = np.std(kohshien_df['winning_count'])

kohshien_df['勝利数偏差値'] = kohshien_df[['winning_count']].apply(winning_deviation, axis=1)
kohshien_df['rate'] = kohshien_df[['勝利数偏差値']].apply(add_rate, axis=1)

kohshien_df['攻撃力ランク'] = kohshien_df[['score','given_point','rate']].apply(attack_rank, axis=1)    
kohshien_df['防御力ランク'] = kohshien_df[['score','given_point','rate']].apply(defence_rank, axis=1)
kohshien_df['優勝回数'] = 0
kohshien_df['lose'] = False
kohshien_df.set_index('name')
kohshien_df[['name','score','given_point','攻撃力ランク','防御力ランク']]

# 検証用パラメータ
# 期待値で検証するかどうか
is_expect = False
# 地域戦力差を考慮するか設定
is_region = True
# 組み合わせをシャッフルするかどうか
is_shuffle = False
# 残りチーム数を設定(1なら優勝チーム、8ならベスト8まで検証)
remain_team = 1
# 何回検証するか設定
limit = 1

# 終了フラグ
end = False
# 　何回戦か
round = 1
# ループ数
loop_count = 1

# 初戦設定(シード除外)
battle_df = kohshien_df[kohshien_df.entry_round == 1].reset_index()

while end == False:
    # 何回戦か表示する
    team_count = kohshien_df['lose'] == False
    if team_count.sum() == 2:
        print("決勝戦")
    elif team_count.sum() == 4:
        print("準決勝")
    elif team_count.sum() == 8:
        print("準々決勝")
    else: 
        print(round, "回戦")

    # シード、負けたチームは対象外
    battle_df = kohshien_df[(kohshien_df.entry_round <= round) & (kohshien_df.lose == False)].reset_index()
    for i in range(len(battle_df)):
        # 2チームで戦うので偶数の時だけ処理
        if i % 2 == 0:
            # 自チームと敵チームのDataFrame作成
            own_df = battle_df[i:i+1]
            other_df = battle_df[i+1:i+2]
        
            # 最大得点を取得 自チームの攻撃値+敵チームの防御値
            own_max = battle_df.loc[own_df.index,'score'].values +  battle_df.loc[other_df.index,'given_point'].values
            other_max =  battle_df.loc[other_df.index,'score'].values + battle_df.loc[own_df.index,'given_point'].values
            # 地域戦力差を考慮
            if is_region == True:
                own_max = own_max * own_df['rate'].values
                other_max = other_max * other_df['rate'].values

            settle = False
            # 期待値で計算(引き分けた場合は乱数で勝負)
            if is_expect == True:
                print("期待値で検証")
                own_score = own_max / 2
                other_score = other_max / 2
                # int型に変換
                own_score = int(np.round(own_score, 0))
                other_score = int(np.round(other_score, 0))
                if (own_score != other_score):
                    settle = True

            # 決着がつくまで繰り返す
            while settle == False:
                # [0～最大得点]の乱数を取得
                own_score = random.uniform(0.0, own_max)
                other_score = random.uniform(0.0, other_max)
                # int型に変換
                own_score = int(np.round(own_score, 0))
                other_score = int(np.round(other_score, 0))
                if (own_score != other_score):
                    # 決着
                    settle = True
                else:
                    # スコアが同じだった場合は再試合
                    print (battle_df.loc[i,'name'], own_score, "-" , other_score, battle_df.loc[i+1,'name'])
                    print ("引き分け再試合！")

            # 対戦結果
            print (battle_df.loc[i,'name'], own_score, "-" , other_score, battle_df.loc[i+1,'name'])

            # 負け判定更新
            if own_score > other_score:
                kohshien_df.loc[other_df['index'].values,'lose'] = True
            else:
                kohshien_df.loc[own_df['index'].values,'lose'] = True

    print ("\n")
    # 何回戦目かをカウントアップ
    round += 1
    # 残りチーム数をカウント
    s_remain = kohshien_df['lose'] == False
    # 残りチームが1チームのみだったら終了
    if s_remain.sum() == remain_team:
        # 優勝チームを出力
        # winner = battle_df[battle_df.lose == False]
        # print (winner.loc[0, 'name'], "が優勝！","\n")
        winner = kohshien_df[kohshien_df.lose == False]
        print (winner.iat[0,0], "が優勝！","\n")
        # 勝利数カウントアップ
        kohshien_df.loc[winner.index.values,'優勝回数'] = kohshien_df.loc[winner.index.values,'優勝回数'] + 1

        # 検証回数カウントアップ
        loop_count += 1
        if loop_count > limit:
            # 検証終了
            end = True
        else:
            #  1回戦目に初期化
            round = 1
            # 勝敗状況初期化
            kohshien_df['lose'] = False
            # 組み合わせシャッフル
            if is_shuffle == True:
                kohshien_df.reindex(np.random.permutation(kohshien_df.index))
                kohshien_df = kohshien_df.reindex(np.random.permutation(kohshien_df.index)).reset_index(drop=True)

            # Dataframe初期化
            # battle_df = kohshien_df[(kohshien_df.entry_round == 1) & (kohshien_df.lose == False)].reset_index()
            print(loop_count,"週目")
            # 1回戦に初期化
            round = 1

# 優勝回数でソート
df_s = kohshien_df.sort_values('優勝回数', ascending=False)

# 優勝回数順に表示
df_s[['name','攻撃力ランク','防御力ランク','優勝回数']]


