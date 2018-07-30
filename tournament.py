import random
import pandas as pd
from pandas import Series, DataFrame

kohshien_df = pd.read_csv('kohshien_sub.csv', encoding="shift-jis")

def attack_rank(score):
    attack, defence = score
    if attack >= 12:
        return 'S'
    elif attack >= 9:
        return 'A'
    elif attack >= 6:
        return 'B'
    elif attack >= 3:
        return 'C'
    else:
        return 'D'
    
def defence_rank(score):
    attack, defence = score
    if defence <= 2:
        return 'S'
    elif defence <= 4:
        return 'A'
    elif defence <= 6:
        return 'B'
    elif defence <= 8:
        return 'C'
    else:
        return 'D'    
    
kohshien_df['攻撃力ランク'] = kohshien_df[['attack','defence']].apply(attack_rank, axis=1)    
kohshien_df['防御力ランク'] = kohshien_df[['attack','defence']].apply(defence_rank, axis=1)
kohshien_df.set_index('name')
kohshien_df[['name','attack','defence','攻撃力ランク','防御力ランク']]

battle_df = kohshien_df[(kohshien_df.seed != True) & (kohshien_df.lose == False)].reset_index()

end = False
count = 1
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
        print(count, "回戦")

    for i in range(len(battle_df)):
        # 2チームで戦うので偶数の時だけ処理
        if i % 2 == 0:
            # 自チームと敵チームのDataFrame作成
            own_df = battle_df[i:i+1]
            other_df = battle_df[i+1:i+2]
        
            # 最大得点を取得 自チームの攻撃値+敵チームの防御値
            own_max = battle_df.loc[own_df.index,'attack'].values +  battle_df.loc[other_df.index,'defence'].values
            other_max =  battle_df.loc[other_df.index,'attack'].values + battle_df.loc[own_df.index,'defence'].values
    
            # 決着がつくまで繰り返す
            settle = False
            while settle == False:
                # [0～最大得点]の乱数を取得
                own_score = random.randrange(own_max)
                other_score = random.randrange(other_max)
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

            # シードは初回のみなのでシードだった場合はFalseに更新
            if kohshien_df.loc[own_df['index'].values,'seed'].values == True:
                kohshien_df.loc[own_df['index'].values,'seed'] = False
            if kohshien_df.loc[other_df['index'].values,'seed'].values == True:
                kohshien_df.loc[other_df['index'].values,'seed'] = False
            print ("\n")
    # 負けたチームを省き、シードを含めた形で再設定
    battle_df = kohshien_df[kohshien_df.lose == False].reset_index()
    # 負けていないチーム数をカウント
    s_bool = kohshien_df['lose'] == False
    # 負けていないチームが1チームのみだったら終了
    if s_bool.sum() == 1:
        # 優勝チームを出力
        winner = battle_df[battle_df.lose == False]
        print (winner.loc[0, 'name'], "が優勝！")
        # whileループを抜ける
        end = True