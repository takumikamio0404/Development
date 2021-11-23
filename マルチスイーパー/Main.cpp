# include <Siv3D.hpp>
#include <iostream>

/*
9=まだ開いてないマス
10=開いた爆弾のマス
-1=ロックされたマス
ウィンドウサイズ：800*600
*/

struct GameData
{
    size_t player_num=2;
    Array<int> gamepads={0,0,0,0};

    const bool debugMode=false;
};
using App=SceneManager<String,GameData>;

class Title:public App::Scene{
    //タイトル画面(人数選択画面)
private:
    const Array<String> options={U"2人",U"3人",U"4人"};
    size_t index;//ラジオボタンで選んでいるインデックス
    
public:
    Title(const InitData& init):IScene(init){
        //人数：2~4、インデックス：0~2だから人数から2引いている
        index=getData().player_num-2;
    }
    void update() override{
        //こうすると自動的にindexの値がラジオボタンと同期する
        if(SimpleGUI::RadioButtons(index,options,Vec2(450,300))){
            getData().player_num=index+2;
        }

        if(SimpleGUI::Button(U"決定",Vec2(350,450))){
            if(getData().debugMode){
                changeScene(U"Game",0.5s);
            }else{
                changeScene(U"Connect",0.5s);//0.5秒使って接続画面に遷移
            }
        }
    }
    void draw() const override{
        Scene::SetBackground(ColorF(0.4,0.7,0.5));
        FontAsset(U"TitleFont")(U"マルチスイーパー").drawAt(400,100);
        FontAsset(U"OtherFont")(U"プレイ人数：").drawAt(350,350);
    }
};

class Connect:public App::Scene{
    //接続待機画面
private:
    const Array<Color> colors={Palette::Lightgrey,Palette::Black,
                               Palette::Lightsalmon,Palette::Red,
                               Palette::Lightgreen,Palette::Green,
                               Palette::Skyblue,Palette::Blue};
    Array<int> states;
    int progress;
    bool ready;
    
public:
    Connect(const InitData& init):IScene(init){
        reset();
    }

    void reset(){
        states={1,0,0,0};//各プレイヤーの進行状況
        getData().gamepads={0,0,0,0};//各プレイヤーの操作コントローラー
        progress=0;//どのプレイヤーまで進んだか
        ready=false;//コントローラーの設定が終わったか
    }

    void update() override{
        if(SimpleGUI::Button(U"タイトルに戻る",Vec2(600,550))){
            changeScene(U"Title",0.5s);
        }
        if(SimpleGUI::Button(U"リセット",Vec2(50,550))){
            reset();
        }
        if(ready){
            if(SimpleGUI::Button(U"ゲーム開始",Vec2(330,550))){
                changeScene(U"Game",0.5s);
            }
        }
        else{
            for(int userIndex=0;userIndex<Gamepad.MaxUserCount;userIndex++){
                //既に登録されているゲームパッドは登録させない
                bool check=true;
                for(int i=0;i<progress;i++){
                    if(getData().gamepads[i]==userIndex){
                        check=false;
                    }
                }
                if(check){
                    if(const auto gamepad=Gamepad(userIndex)){
                        //何かしらのボタンが押されているかどうか
                        bool buttonPressedCheck=false;
                        for(auto[i,button]:Indexed(gamepad.buttons)){
                            if(button.pressed()){
                                buttonPressedCheck=true;
                                break;
                            }
                        }
                        if(buttonPressedCheck){
                            getData().gamepads[progress]=userIndex;
                            states[progress]=2;
                            progress++;
                            if(progress==getData().player_num){
                                ready=true;
                                break;
                            }
                            states[progress]=1;
                            break;
                        }
                    }
                }
            }
        }
    }
    void draw() const override{
        Scene::SetBackground(ColorF(0.4,0.7,0.5));
        FontAsset(U"OtherFont")(U"待機画面").drawAt(400,50);
        for(int i=0;i<getData().player_num;i++){
            const Rect rect(80+(i%2)*340,100+(i/2)*240,300,200);
            rect.draw(colors[i*2]);
            rect.drawFrame(1,1,colors[i*2+1]);
            FontAsset(U"OtherFont")(U"{}P"_fmt(i+1)).drawAt(110+(i%2)*340,120+(i/2)*240,Palette::Black);
            if(states[i]==0){
                FontAsset(U"TextFont")(U"待機").drawAt(230+(i%2)*340,200+(i/2)*240,Palette::Black);
            }
            else if(states[i]==1){
                FontAsset(U"TextFont")(U"使うゲームパッドのボタンを\n何か押してください").drawAt(230+(i%2)*340,200+(i/2)*240,Palette::Black);
            }
            else if(states[i]==2){
                String text;
                if(const auto gamepad=Gamepad(getData().gamepads[i])){
                    text=U"ゲームパッド{}\n{}"_fmt(getData().gamepads[i],gamepad.getInfo().name);
                }else{
                    text=U"ゲームパッド{}"_fmt(getData().gamepads[i]);
                }
                FontAsset(U"TextFont")(text).drawAt(230+(i%2)*340,200+(i/2)*240,Palette::Black);
            }
        }
    }
};

class Game:public App::Scene{
private:
    const Array<Color> colors={Palette::Lightgrey,Palette::Black,
                               Palette::Lightsalmon,Palette::Red,
                               Palette::Lightgreen,Palette::Green,
                               Palette::Skyblue,Palette::Blue};
    const int p_num= (int)getData().player_num;
    int winner;

    Array<Vec2> cursorPoses;
    Array<Grid<int>> field;
    Array<Grid<int>> bombs;
    Array<int> playerAttack;
    Array<bool> buttonPush;
    Array<bool> playerAlive;
    
    Array<int> countRocks;

    Array<double> stunStartTimes;
    Array<bool> isStun;

    bool gameFinished;
    
public:
    //コンストラクタ
    Game(const InitData& init):IScene(init){
        for(int i=0;i<p_num;i++){
            cursorPoses<<Vec2(268+264*(i%2),144+264*(i/2));
        }
        for(int i=0;i<p_num;i++){
            field<<Grid<int>(10,10,9);
        }
        for(int i=0;i<p_num;i++){
            Grid<int> grid = Grid<int>(10, 10, 0);
            Array<int> list;
            for(int y=0;y<10;y++){
                for(int x=0;x<10;x++){
                    if(!(3<=x && x<=6 && 3<=y &&y<=6)){
                        list<<10*y+x;
                    }
                }
            }
            list=list.choice(16);
            for(int bombNum:list){
                grid[bombNum/10][bombNum%10]=1;
            }
            bombs << grid;
        }
        for(int playerID=0;playerID<p_num;playerID++){
            for(int y=3;y<=6;y++){
                for(int x=3;x<=6;x++){
                    field[playerID][y][x]=bombCount(playerID,x,y);
                }
            }
        }
        playerAttack=Array<int>(p_num,3);
        countRocks=Array<int>(p_num,0);
        buttonPush=Array<bool>(p_num,false);
        playerAlive=Array<bool>(p_num,true);
        stunStartTimes = Array<double>(p_num, 0);
        isStun = Array<bool>(p_num, false);
        gameFinished=false;
    }

    //指定されたマスの周囲の爆弾を数える関数
    int bombCount(int playerID,int x,int y){
        int count=0;
        for(int b=y-1;b<y+2;b++){
            if(0<=b && b<10){
                for(int a=x-1;a<x+2;a++){
                    if(0<=a && a<10){
                        if(bombs[playerID][b][a]==1){
                            count++;
                        }
                    }
                }
            }
        }
        return count;
    }

    //マスを開ける関数
    bool cellOpen(int playerID,int x,int y){
        if(bombs[playerID][y][x]==1){
            playerAlive[playerID]=false;
            field[playerID][y][x]=10;
            return true;
        }
        else{
            int count=bombCount(playerID,x,y);
            field[playerID][y][x]=count;
            //0開け
            if(count==0){
                for(int b=y-1;b<y+2;b++){
                    if(0<=b && b<10){
                        for(int a=x-1;a<x+2;a++){
                            if(0<=a && a<10){
                                if(field[playerID][b][a]==9){
                                    cellOpen(playerID,a,b);
                                }
                            }
                        }
                    }
                }
            }
            return false;
        }
    }

    //周りの、爆弾の数とロックされたマスの数が同じであれば周りのロックされていないマスを開ける関数
    void numberOpen(const int playerID,const int x,const int y){
        int num=field[playerID][y][x];
        for(int b=y-1;b<y+2;b++){
            if(0<=b && b<10){
                for(int a=x-1;a<x+2;a++){
                    if(0<=a && a<10){
                        if(field[playerID][b][a]==-1){
                            num--;
                        }
                    }
                }
            }
        }
        if(num!=0)return;
        for(int b=y-1;b<y+2;b++){
            if(0<=b && b<10){
                for(int a=x-1;a<x+2;a++){
                    if(0<=a && a<10){
                        if(field[playerID][b][a]==9){
                            cellOpen(playerID,a,b);
                        }
                    }
                }
            }
        }
    }

    //試合が終わったかをチェックする関数
    void finishCheck(){
        int aliveCount=0;
        int aliveID=0;
        for(int i=0;i<p_num;i++){
            if(playerAlive[i]){
                aliveID=i;
                aliveCount++;
            }
        }
        if(aliveCount==1){
            gameFinished=true;
            winner=aliveID;
            return;
        }
        bool isClear;
        for(int playerID=0;playerID<p_num;playerID++){
            if(!playerAlive[playerID])continue;
            isClear=true;
            for(int y=0;y<10;y++){
                for(int x=0;x<10;x++){
                    if(bombs[playerID][y][x]==0 && (field[playerID][y][x]==-1 || field[playerID][y][x]==9)){
                        isClear=false;
                        break;
                    }
                }
                if(!isClear)break;
            }
            if(isClear){
                gameFinished=true;
                winner=playerID;
                return;
            }
        }
    }

    void open(int playerID, int x, int y){
        for(int j=0;j<getData().player_num;j++){
            if(148+264*(j%2)<x && x<388+264*(j%2) && 24+264*(j/2)<y && y<264+264*(j/2)){
                if (!playerAlive[j])break;
                x-=148+264*(j%2);
                y-=24+264*(j/2);
                x/=24;
                y/=24;
                //自陣
                if(playerID ==j){
                    if(field[j][y][x]==9){
                        cellOpen(j,x,y);
                    }
                    else if(field[j][y][x]!=-1 && field[j][y][x]!=10){
                        numberOpen(j,x,y);
                    }
                //敵陣
                }else{
                    if(field[j][y][x]==9){
                        if(playerAttack[playerID]>0){
                            if (!cellOpen(j, x, y)) {
                                playerAttack[playerID]--;
                                isStun[playerID] = true;
                                stunStartTimes[playerID] = Scene::Time();
                            }
                        }
                    }
                }
                finishCheck();
                break;
            }
        }
    }

    void update() override{
        if(SimpleGUI::Button(U"タイトルに戻る",Vec2(600,550))){
            changeScene(U"Title",0.5s);
        }
        if(SimpleGUI::Button(U"リセット",Vec2(200,550))){
            changeScene(U"Game",0.5s);
        }
        if(getData().debugMode && SimpleGUI::Button(U"マス開け",Vec2(400,550))){
            field[0][1][5]=-1;
            field[0][7][2]=-1;
            field[0][8][9]=-1;
            cellOpen(0,0,0);
            cellOpen(0,5,0);
            cellOpen(0,0,5);
            for (int i = 0;i < getData().player_num;i++) {
                //Print << i;
                isStun[i] = true;
                stunStartTimes[i] = Scene::Time();
            }
        }
        if(gameFinished)return;
        for(int i=0;i<getData().player_num;i++){
            if(!playerAlive[i]){
                cursorPoses[i]=Vec2(0,0);
                continue;
            }
            if (isStun[i]) {
                if (Scene::Time() - stunStartTimes[i] > 5) {
                    isStun[i] = false;
                }
                continue;
            }
            if(const auto gamepad=Gamepad(getData().gamepads[i])){
                for(auto[j,axe]:Indexed(gamepad.axes)){
                    if(j%2==0){
                        cursorPoses[i].x+=axe*2;
                    }else{
                        cursorPoses[i].y+=axe*2;
                    }
                }
                //Aボタンが押されたら(マス開け処理)
                if(!buttonPush[i] && gamepad.buttons[0].pressed()){
                    buttonPush[i]=true;
                    int x=(int)cursorPoses[i].x;
                    int y=(int)cursorPoses[i].y;
                    open(i, x, y);
                }
                //Bボタンが押されたら(ロック処理)
                else if(!buttonPush[i] && gamepad.buttons[1].pressed()){
                    buttonPush[i]=true;
                    int x=(int)cursorPoses[i].x;
                    int y=(int)cursorPoses[i].y;
                    //自陣以外の場所ではロックできないからiに限定している
                    if(148+264*(i%2)<x && x<388+264*(i%2) && 24+264*(i/2)<y && y<264+264*(i/2)){
                        x-=148+264*(i%2);
                        y-=24+264*(i/2);
                        x/=24;
                        y/=24;
                        if(field[i][y][x]==9){
                            field[i][y][x]=-1;
                            countRocks[i]++;
                        }else if(field[i][y][x]==-1){
                            field[i][y][x]=9;
                            countRocks[i]--;
                        }else{
                            int num=field[i][y][x];
                            for(int b=y-1;b<y+2;b++){
                                if(0<=b && b<10){
                                    for(int a=x-1;a<x+2;a++){
                                        if(0<=a && a<10){
                                            if(field[i][b][a]==-1 || field[i][b][a]==9){
                                                num--;
                                            }
                                        }
                                    }
                                }
                            }
                            if(num!=0)return;
                            for(int b=y-1;b<y+2;b++){
                                if(0<=b && b<10){
                                    for(int a=x-1;a<x+2;a++){
                                        if(0<=a && a<10){
                                            if(field[i][b][a]==9){
                                                field[i][b][a]=-1;
                                                countRocks[i]++;
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                    
                }else if(!buttonPush[i] && gamepad.buttons[2].pressed()){
                    buttonPush[i]=true;
                    cursorPoses[i]=Vec2(168+264*(i%2),168+264*(i/2));                        
                }else if(!buttonPush[i] && gamepad.povD8()!=none){
                    buttonPush[i]=true;
                    switch(gamepad.povD8().value()){
                        case 0:
                        cursorPoses[i].y-=264;
                        break;
                        case 2:
                        cursorPoses[i].x+=264;
                        break;
                        case 4:
                        cursorPoses[i].y+=264;
                        break;
                        case 6:
                        cursorPoses[i].x-=264;
                        break;
                    }
                }else if(buttonPush[i] && !gamepad.buttons[0].pressed() && !gamepad.buttons[1].pressed() && !gamepad.buttons[2].pressed() && gamepad.povD8()==none){
                    buttonPush[i]=false;
                }
            }
        }
    }
    void draw() const override{
        for(int i=0;i<getData().player_num;i++){
            for(int y=0;y<10;y++){
                for(int x=0;x<10;x++){
                    //爆ぜた爆弾マス
                    if(field[i][y][x]==10){
                        Rect(148+264*(i%2)+x*24,24+264*(i/2)+y*24,24,24)
                        .draw(Palette::Lightgrey)
                        .drawFrame(1,1,Palette::Black);
                        Circle(160+264*(i%2)+x*24,36+264*(i/2)+y*24,10)
                        .draw(Palette::Black);
                    }
                    //開いてないマス
                    else if(field[i][y][x]==9){
                        Color color=playerAlive[i]?Palette::Green:Palette::Gray;
                        Rect(148+264*(i%2)+x*24,24+264*(i/2)+y*24,24,24)
                        .draw(color)
                        .drawFrame(1,1,Palette::Black);
                        if(!playerAlive[i] && bombs[i][y][x]==1){
                            Circle(160+264*(i%2)+x*24,36+264*(i/2)+y*24,10)
                            .draw(Palette::Black);
                        }
                    }
                    //ロックされたマス
                    else if(field[i][y][x]==-1){
                        Color color=playerAlive[i]?Palette::Lightsalmon:Palette::Darkgray;
                        Rect(148+264*(i%2)+x*24,24+264*(i/2)+y*24,24,24)
                        .draw(color)
                        .drawFrame(1,1,Palette::Black);
                        if(!playerAlive[i]){
                            if(bombs[i][y][x]==1){
                                Circle(160+264*(i%2)+x*24,36+264*(i/2)+y*24,10)
                                .draw(Palette::Black);
                            }else{
                                Line(148+264*(i%2)+x*24,24+264*(i/2)+y*24,148+264*(i%2)+(x+1)*24,24+264*(i/2)+(y+1)*24)
                                .draw(Palette::Black);
                                Line(148+264*(i%2)+(x+1)*24,24+264*(i/2)+y*24,148+264*(i%2)+x*24,24+264*(i/2)+(y+1)*24)
                                .draw(Palette::Black);
                            }
                        }
                    }
                    //開いているマス(数字マス)
                    else{
                        Color color=playerAlive[i]?Palette::Lightgreen:Palette::Lightgrey;
                        Rect(148+264*(i%2)+x*24,24+264*(i/2)+y*24,24,24)
                        .draw(color)
                        .drawFrame(1,1,Palette::Black);
                        FontAsset(U"TextFont")(U"{}"_fmt(field[i][y][x])).drawAt(160+264*(i%2)+x*24,36+264*(i/2)+y*24,Palette::Black);
                    }
                }
            }
        }
        //カーソル
        for(int i=0;i<getData().player_num;i++){
            Circle(cursorPoses[i],5).draw(colors[2*i+1]);
        }
        //残弾
        for(int i=0;i<getData().player_num;i++){
            FontAsset(U"TextFont")(U"{}/16"_fmt(countRocks[i])).drawAt(120+560*(i%2),256+260*(i/2),Palette::Black);
            FontAsset(U"TextFont")(U"残り{}回"_fmt(playerAttack[i])).drawAt(115+570*(i%2),36+260*(i/2),Palette::Black);
        }
        //スタン
        for (int i = 0;i < getData().player_num;i++) {
            if (isStun[i]) {
                FontAsset(U"TextFont")(U"スタン！").drawAt(100 + 600 * (i % 2), 80 + 260 * (i / 2), Palette::Black);
            }
        }
        //勝利判定
        if(gameFinished){
            FontAsset(U"TextFont")(U"プレイヤー{}の勝利"_fmt(winner)).drawAt(300,10,Palette::Black);
        }
    }
};

void Main()
{
    FontAsset::Register(U"TitleFont",60,Typeface::Heavy);
    FontAsset::Register(U"OtherFont",30,Typeface::Bold);
    FontAsset::Register(U"TextFont",15);

    App manager;
    manager.add<Title>(U"Title");
    manager.add<Connect>(U"Connect");
    manager.add<Game>(U"Game");
    manager.setFadeColor(ColorF(0.4,0.7,0.5));
    while (System::Update()){
        if(!manager.update()){
            break;
        }
    }
}