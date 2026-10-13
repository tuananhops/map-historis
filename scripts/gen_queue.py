"""Builds map-only (no media needed) topic JSONs into topics/queue/ from compact, fact-checked data.
Beat = (lon,lat,k, year, caption, color, text, armies[(from,to,color)], pins[(ll,label)], xstamp_ll|None, counter|None)"""
import json, os, re, sys, unicodedata
B=os.path.dirname(os.path.abspath(__file__)); WD=os.environ.get("WORK_DIR",os.path.join(B,"work")); Q=f"{WD}/topics/queue"; os.makedirs(Q,exist_ok=True)
_R=os.environ.get("REGISTRY",f"{WD}/topics_done.json"); DONE=json.load(open(_R))["done"] if os.path.exists(_R) else []
CRED="Ảnh vệ tinh: NASA Blue Marble · ranh giới minh hoạ"
BASE_SPELL={"Hinton":"hin tơn","Media":"mê đi a","TCN":"trước công nguyên"}
def topic(slug,title,layer,hook,beats,spell={},hs=False):
    lon,lat,_=beats[-1][:3]; sc=[{"name":"hook","type":"intro","to":list(beats[0][:2]),"R":4800,"title":"Bạn có biết?","text":hook}]
    for i,(x,y,k,yr,cap,colr,text,arm,pins,xs,cnt) in enumerate(beats):
        p=beats[i-1] if i else (x+1.5,y-0.8,k*0.6)
        S={"name":f"b{i}","type":"map","layers":[layer] if layer else [],"cam":[[0,p[0],p[1],min(p[2],k)*0.85],[0.5,(p[0]+x)/2,(p[1]+y)/2,k*0.9],[1,x,y,k]],
           "hud":{"year":yr,"caption":cap,"color":colr},"text":text,"start":" ".join(text.split()[:4]),
           "armies":[{"from":list(a),"to":list(b),"at":0.3+0.35*j,"dur":1.3,"n":40,"color":c,"seed":i*5+j,"bend":0.12*(-1)**j} for j,(a,b,c) in enumerate(arm)],
           "pins":[{"ll":list(ll),"at":0.2+0.3*j,"label":lb,"color":"gold" if j==0 else "orange","dy":-62 if j%2==0 else 62} for j,(ll,lb) in enumerate(pins)],
           "sfx":[{"kind":"drum","at":0.1},{"kind":"whoosh","at":0.5}]}
        if hs: S["hs_ts"]=True
        if xs: S["xstamps"]=[{"ll":list(xs),"at":2.2}]
        if cnt: S["counter"]={"value":cnt[0],"label":cnt[1],"color":"white","at":2.6}; S["sfx"].append({"kind":"boom","at":2.6})
        sc.append(S)
    sc.append({"name":"outro","type":"outro","from":[lon,lat],"start":"Lịch sử thế giới","text":"Lịch sử thế giới qua bản đồ. Theo dõi Hinton Media để xem thêm."})
    words=sum(len(s["text"].split()) for s in sc)
    T={"title":title,"brand":"HINTON MEDIA","music":"epic","duration_range":[28,68],"media_dir":"","exclude_countries":[],"sat_regions":{},
       "map_credit":CRED,"scenes":sc,"spell":{**BASE_SPELL,**spell},"_words":words,"_source":"gen_queue.py (map-only, facts: standard encyclopedic accounts)"}
    return slug,T
R="red";G="gold";Bl="blue";O="orange"
TOP=[
topic("tours_732","Tours 732","BME","Bạn có biết? Năm 732, một trận đánh ở miền trung nước Pháp đã chặn bước tiến của quân Umayyad vào châu Âu.",[
 (0.0,44.5,22,"732","Vượt Pyrenees",R,"Từ Tây Ban Nha, quân Umayyad do Abd al Rahman chỉ huy vượt dãy Pyrenees, cướp phá xứ Aquitaine và tiến về phía bắc.",[((-1.5,43.0),(0.3,46.0),R)],[((-0.58,44.84),"Bordeaux")],None,None),
 (0.7,47.0,40,"732","Giữa Tours và Poitiers",O,"Charles Martel, thủ lĩnh người Frank, dàn quân bộ binh thành khối vững chắc giữa Tours và Poitiers, chờ đối phương tấn công.",[((2.5,48.0),(0.8,47.0),Bl)],[((0.69,47.39),"Tours"),((0.34,46.58),"Poitiers")],None,None),
 (0.5,46.8,50,"732","Tường khiên",G,"Kỵ binh Umayyad xung phong nhiều lần nhưng không phá được bức tường khiên. Abd al Rahman tử trận, quân Umayyad rút lui trong đêm.",[((0.0,46.5),(0.5,46.8),R)],[],(0.5,46.8),None),
 (1.0,47.5,30,"732","Charles Martel",G,"Charles Martel được gọi là Cái Búa. Cháu nội ông là Charlemagne sau này lập nên đế chế Frank hùng mạnh nhất Tây Âu.",[],[((0.69,47.39),"Tours")],None,None)],
 {"Umayyad":"u mai át","Abd":"áp","al":"an","Rahman":"ra man","Pyrenees":"pi rê nê","Aquitaine":"a ki ten","Charles":"sạc","Martel":"mác ten","Frank":"phrăng","Tours":"tua","Poitiers":"poa chi ê","Charlemagne":"sạc lơ ma nhơ","Bordeaux":"bo đô"}),
topic("zama_202bc","Zama 202 TCN","","Bạn có biết? Năm 202 TCN, Hannibal, người từng đánh bại La Mã nhiều lần, đã thua trận quyết định ngay trên đất châu Phi.",[
 (12.5,40.0,14,"218 TCN","Vượt Alps",R,"Hơn mười lăm năm trước, Hannibal vượt dãy Alps đánh vào Ý và gây cho La Mã những thất bại nặng nề.",[((2.0,41.5),(9.0,45.0),R),((9.0,45.0),(12.5,42.0),R)],[((12.48,41.9),"La Mã")],None,None),
 (10.0,37.0,20,"204 TCN","Scipio đổ bộ",Bl,"Tướng La Mã Scipio không đánh ở Ý mà đổ bộ sang châu Phi, đe doạ thẳng thủ đô Carthage. Hannibal buộc phải về cứu.",[((12.0,38.0),(10.0,37.0),Bl)],[((10.32,36.85),"Carthage")],None,None),
 (9.4,36.2,32,"202 TCN","Zama",O,"Tại Zama, Hannibal tung voi chiến lên trước. Quân La Mã mở các hành lang để voi chạy qua, khiến đòn mở màn mất tác dụng.",[((9.2,36.1),(9.5,36.25),R)],[((9.43,36.2),"Zama")],None,None),
 (9.4,36.2,34,"202 TCN","Kỵ binh đánh hậu",G,"Kỵ binh Numidia đồng minh của Scipio quay lại đánh vào sau lưng quân Carthage. Hannibal thất bại, Carthage phải cầu hoà và mất vị thế cường quốc.",[((9.7,36.4),(9.4,36.2),G)],[],(9.4,36.2),None)],
 {"Hannibal":"han ni ban","Scipio":"xi pi ô","Carthage":"các ta giơ","Zama":"da ma","Alps":"an pơ","Numidia":"nu mi đi a"}),
topic("teutoburg_9","Rừng Teutoburg năm 9","BME","Bạn có biết? Năm 9, ba quân đoàn La Mã đã biến mất trong một khu rừng ở nước Đức ngày nay.",[
 (8.5,51.5,22,"Năm 9","Germania",R,"Thống đốc Varus dẫn ba quân đoàn La Mã đóng ở vùng Germania, tin tưởng hoàn toàn vào Arminius, một thủ lĩnh người German phục vụ La Mã.",[((6.5,51.0),(8.5,52.0),R)],[((8.9,52.4),"Varus")],None,None),
 (8.1,52.4,45,"Năm 9","Phục kích",O,"Arminius bí mật liên kết các bộ tộc, dụ Varus đi qua vùng rừng rậm và đầm lầy gần Kalkriese, nơi đội hình La Mã bị kéo dài.",[((8.6,52.5),(8.1,52.4),G),((7.8,52.6),(8.1,52.4),G)],[((8.13,52.41),"Kalkriese")],None,None),
 (8.1,52.4,55,"Năm 9","Ba ngày",R,"Trong mưa gió, quân La Mã bị tấn công suốt nhiều ngày. Varus tự sát, ba quân đoàn mười bảy, mười tám và mười chín bị tiêu diệt.",[],[],(8.1,52.4),(3,"quân đoàn bị xoá sổ")),
 (8.0,51.0,18,"Sau năm 9","Sông Rhine",Bl,"Hoàng đế Augustus được kể là đã kêu lên: Varus, trả lại quân đoàn cho ta! La Mã từ đó không còn chinh phục lâu dài vùng đất phía đông sông Rhine.",[],[((6.95,50.94),"Rhine")],None,None)],
 {"Teutoburg":"tôi tô bua","Varus":"va rút","Germania":"giec ma ni a","Arminius":"ác mi ni út","German":"giec man","Kalkriese":"can kri dơ","Augustus":"au gút tút","Rhine":"rai nơ"}),
topic("chalons_451","Đồng Catalaunum 451","BME","Bạn có biết? Năm 451, Attila và người Hun đã bị chặn lại giữa lòng xứ Gaul.",[
 (12.0,48.0,10,"451","Người Hun",R,"Attila, vua người Hun, dẫn một liên quân lớn vượt sông Rhine tràn vào xứ Gaul, đánh phá nhiều thành phố.",[((16.0,48.5),(8.0,49.5),R)],[((7.6,49.0),"Rhine")],None,None),
 (2.0,47.9,30,"451","Orléans",O,"Attila vây Orléans. Tướng La Mã Aetius liên minh với vua người Visigoth là Theodoric để giải vây.",[((1.0,46.0),(1.9,47.9),Bl)],[((1.9,47.9),"Orléans")],None,None),
 (4.4,48.9,40,"451","Catalaunum",G,"Hai bên gặp nhau ở cánh đồng Catalaunum, gần Châlons ngày nay. Trận chiến đẫm máu, vua Theodoric tử trận.",[((4.0,48.6),(4.4,48.9),Bl),((4.9,49.1),(4.4,48.9),R)],[((4.37,48.95),"Châlons")],(4.4,48.9),None),
 (4.4,48.9,20,"451","Rút lui",Bl,"Attila phải rút khỏi xứ Gaul. Đây là một trong những trận đánh lớn cuối cùng của Đế quốc Tây La Mã.",[((4.4,48.9),(9.0,49.5),R)],[],None,None)],
 {"Attila":"át ti la","Hun":"hun","Gaul":"gôn","Rhine":"rai nơ","Orléans":"oóc lê ăng","Aetius":"a ê ti út","Visigoth":"vi di gốt","Theodoric":"tê ô đô ríc","Catalaunum":"ca ta lau num","Châlons":"sa lông"}),
topic("crecy_1346","Crécy 1346","BME","Bạn có biết? Năm 1346, cung thủ Anh đã đánh gục kỵ sĩ Pháp ở Crécy.",[
 (0.5,49.4,25,"1346","Đổ bộ Normandy",R,"Trong Chiến tranh Trăm năm, vua Edward đệ Tam của Anh đổ bộ lên Normandy rồi tiến về phía bắc nước Pháp.",[((-1.3,49.6),(1.5,50.0),R)],[((-1.27,49.6),"Normandy")],None,None),
 (1.9,50.25,48,"1346","Crécy",O,"Tại Crécy, quân Anh chọn thế đồi, dàn cung thủ trường cung hai bên sườn, kỵ sĩ xuống ngựa đứng giữa.",[],[((1.88,50.25),"Crécy")],None,None),
 (1.9,50.25,55,"1346","Mưa tên",G,"Lính nỏ thuê của Pháp bắn chậm hơn nhiều. Kỵ sĩ Pháp xung phong liên tục lên dốc và bị mưa tên quật ngã.",[((1.75,50.15),(1.88,50.25),Bl)],[],(1.88,50.24),None),
 (1.85,50.95,30,"1347","Calais",R,"Anh thắng lớn rồi tiến đánh Calais. Sau gần một năm vây hãm, Calais thuộc về Anh trong hơn hai trăm năm.",[((1.9,50.25),(1.85,50.95),R)],[((1.85,50.95),"Calais")],None,None)],
 {"Crécy":"cờ rê xi","Edward":"ét uốt","Normandy":"noóc măng đi","Calais":"ca le"}),
topic("grunwald_1410","Grunwald 1410","","Bạn có biết? Năm 1410, một trong những trận đánh lớn nhất châu Âu trung cổ đã bẻ gãy sức mạnh Hiệp sĩ Teuton.",[
 (21.0,53.0,14,"1409","Chiến tranh",R,"Hiệp sĩ Teuton cai trị vùng Phổ ven biển Baltic và tranh chấp đất đai với Ba Lan và Litva.",[],[((19.03,54.04),"Marienburg")],None,None),
 (20.1,53.48,30,"1410","Hợp quân",Bl,"Vua Ba Lan Władysław Jagiełło và đại công tước Litva Vytautas hợp quân, tiến thẳng về phía thủ phủ của Hiệp sĩ.",[((21.0,52.5),(20.1,53.45),Bl),((22.5,53.0),(20.2,53.5),G)],[((20.1,53.48),"Grunwald")],None,None),
 (20.1,53.48,36,"15/7/1410","Grunwald",O,"Ngày mười lăm tháng bảy, hai bên giao chiến. Quân Litva giả rút lui rồi quay lại, trong khi quân Ba Lan giữ vững trung tâm.",[((20.0,53.55),(20.1,53.48),R)],[],None,None),
 (20.1,53.48,36,"1410","Đại thắng",G,"Đại thống lĩnh Ulrich von Jungingen tử trận cùng phần lớn lãnh đạo dòng Hiệp sĩ. Từ đây, Ba Lan và Litva trở thành thế lực mạnh ở Đông Âu.",[],[],(20.1,53.5),None)],
 {"Teuton":"tơ tông","Baltic":"ban tích","Marienburg":"ma ri en bua","Władysław":"voa đi xoáp","Jagiełło":"gia ghi eo","Vytautas":"vi tau tát","Grunwald":"grun van","Ulrich":"un rích","von":"phôn","Jungingen":"dung ing ghen","Litva":"lít va","Phổ":"phổ"}),
topic("orleans_1429","Jeanne d'Arc giải vây Orléans 1429","BME","Bạn có biết? Năm 1429, một cô gái mười bảy tuổi đã xoay chuyển Chiến tranh Trăm năm.",[
 (1.9,47.9,30,"1428","Vây Orléans",R,"Quân Anh vây Orléans, cửa ngõ dẫn xuống miền nam nước Pháp. Nếu thành mất, phe vua Charles đệ Thất gần như hết hy vọng.",[((1.5,48.5),(1.9,47.95),R)],[((1.9,47.9),"Orléans")],None,None),
 (0.24,47.17,28,"1429","Chinon",G,"Jeanne d'Arc, cô gái nông dân vùng Lorraine, tìm đến Chinon thuyết phục Charles cho cô theo đoàn quân cứu viện.",[],[((0.24,47.17),"Chinon")],None,None),
 (1.9,47.9,50,"5/1429","Giải vây",O,"Tháng năm năm 1429, quân Pháp tấn công các pháo đài của Anh quanh thành. Chỉ trong khoảng chín ngày, vòng vây bị phá.",[((2.0,47.8),(1.9,47.9),Bl)],[],(1.9,47.88),None),
 (4.03,49.25,30,"7/1429","Reims",G,"Sau đó, Charles được đăng quang tại Reims. Jeanne bị bắt năm 1430 và bị xử thiêu năm 1431, nhưng nước Pháp cuối cùng thắng cuộc chiến.",[((1.9,47.9),(4.0,49.2),Bl)],[((4.03,49.25),"Reims")],None,None)],
 {"Jeanne":"gian nơ","d'Arc":"đác","Orléans":"oóc lê ăng","Charles":"sạc","Lorraine":"lo ren","Chinon":"si nông","Reims":"ranh"}),
topic("armada_1588","Hạm đội Tây Ban Nha 1588","","Bạn có biết? Năm 1588, hạm đội bất khả chiến bại của Tây Ban Nha đã thất bại trước Anh và bão biển.",[
 (-6.0,44.0,10,"1588","Ra khơi",R,"Vua Felipe đệ Nhị phái khoảng một trăm ba mươi tàu lên phía bắc, định hộ tống quân từ Hà Lan đổ bộ vào nước Anh.",[((-9.0,43.0),(-4.0,48.5),R)],[((-8.4,43.37),"La Coruña")],None,(130,"chiến thuyền")),
 (-1.0,50.2,18,"1588","Eo biển Manche",Bl,"Hạm đội Anh, nhỏ và nhanh hơn, bám đuổi dọc eo biển Manche và bắn từ xa.",[((-3.0,50.0),(0.5,50.3),Bl)],[((-4.14,50.37),"Plymouth")],None,None),
 (1.9,51.0,30,"8/1588","Thuyền lửa",O,"Tại Calais, người Anh thả thuyền lửa vào ban đêm. Hạm đội Tây Ban Nha cắt neo tháo chạy, rồi bị đánh tiếp ở Gravelines.",[((1.5,51.2),(1.9,51.0),O)],[((1.85,50.95),"Calais")],(2.1,51.0),None),
 (-6.0,56.0,8,"1588","Bão biển",R,"Gió đẩy hạm đội lên phía bắc, vòng quanh Scotland và Ireland. Bão đánh đắm nhiều tàu, số còn lại về nhà trong cảnh tan tác.",[((2.0,52.0),(-1.0,59.0),R),((-1.0,59.0),(-10.0,53.0),R)],[],(-9.5,54.0),None)],
 {"Felipe":"phê li pê","Manche":"mangsơ","Plymouth":"pli mơt","Calais":"ca le","Gravelines":"gra vơ lin","Coruña":"cô ru nha","La":"la","Scotland":"xcốt len","Ireland":"ai len"}),
topic("blenheim_1704","Blenheim 1704","","Bạn có biết? Năm 1704, một cuộc hành quân táo bạo đã cứu Viên và làm rung chuyển nước Pháp của vua Mặt Trời.",[
 (8.0,50.0,12,"1704","Hành quân",Bl,"Công tước Marlborough của Anh bất ngờ dẫn quân từ Hà Lan hành quân hàng trăm cây số xuống sông Danube.",[((5.5,51.5),(10.5,48.7),Bl)],[((10.6,48.65),"Blenheim")],None,None),
 (10.6,48.65,35,"1704","Danube",O,"Ông hợp quân với Hoàng tử Eugene xứ Savoy. Đối diện là quân Pháp và Bavaria, đe doạ trực tiếp thành Viên.",[((11.0,48.5),(10.65,48.62),G)],[],None,None),
 (10.6,48.65,38,"13/8/1704","Blenheim",R,"Ngày mười ba tháng tám, Marlborough dồn lực đánh vào trung tâm quân Pháp, chia cắt đội hình đối phương.",[((10.5,48.6),(10.6,48.65),Bl)],[],(10.6,48.66),None),
 (10.6,48.65,30,"1704","Đầu hàng",G,"Hàng nghìn lính Pháp bị dồn vào làng Blenheim và phải đầu hàng, thống chế Tallard bị bắt. Đây là thất bại lớn đầu tiên của vua Louis mười bốn trong nhiều thập kỷ.",[],[],None,None)],
 {"Marlborough":"mon bơ râu","Danube":"đa nuýp","Eugene":"ơ gien","Savoy":"xa voa","Bavaria":"ba va ri a","Blenheim":"blen hem","Tallard":"ta la","Louis":"lu i"}),
topic("poltava_1709","Poltava 1709","","Bạn có biết? Năm 1709, Thụy Điển mất vị thế cường quốc chỉ sau một buổi sáng ở Ukraine.",[
 (24.0,55.0,9,"1708","Đánh Nga",Bl,"Vua Charles mười hai của Thụy Điển, vị vua trẻ bách chiến, dẫn quân tiến đánh nước Nga của Pyotr Đại đế.",[((18.0,59.3),(28.0,54.0),Bl)],[((18.07,59.33),"Stockholm")],None,None),
 (32.0,51.0,14,"1708–1709","Mùa đông",R,"Nga đốt phá đường tiếp tế, quân Thụy Điển rẽ xuống Ukraine. Mùa đông khắc nghiệt làm hao mòn lực lượng của Charles.",[((28.0,54.0),(34.0,50.0),Bl)],[],None,None),
 (34.55,49.6,35,"8/7/1709","Poltava",O,"Charles bị thương ở chân. Quân Thụy Điển ít hơn nhiều vẫn tấn công các đồn luỹ của Nga ở Poltava.",[((34.5,49.55),(34.6,49.62),Bl)],[((34.55,49.59),"Poltava")],None,None),
 (34.55,49.6,30,"1709","Sụp đổ",R,"Pháo binh và bộ binh Nga đánh bại quân Thụy Điển. Charles trốn sang đế chế Ottoman, còn nước Nga vươn lên thành cường quốc ở Bắc Âu.",[((34.6,49.65),(34.55,49.6),R)],[],(34.55,49.6),None)],
 {"Charles":"sạc","Pyotr":"pi ốt","Poltava":"pôn ta va","Ottoman":"ốt tô man","Stockholm":"xtốc hôm"}),
topic("leipzig_1813","Leipzig 1813","BME","Bạn có biết? Năm 1813, hơn nửa triệu binh sĩ đã đụng độ ở Leipzig, trận đánh lớn nhất châu Âu trước thế kỷ hai mươi.",[
 (25.0,54.0,8,"1812","Thảm hoạ Nga",R,"Sau thảm hoạ ở Nga năm 1812, Napoleon gấp rút xây lại quân đội để giữ nước Đức.",[((37.0,55.7),(20.0,53.0),Bl)],[],None,None),
 (12.37,51.34,25,"10/1813","Liên quân",O,"Nga, Phổ, Áo và Thụy Điển hợp thành liên quân, từ nhiều hướng khép vòng vây quanh Leipzig.",[((13.5,52.0),(12.45,51.38),R),((13.5,50.6),(12.45,51.3),R),((11.5,51.9),(12.32,51.4),R)],[((12.37,51.34),"Leipzig")],None,None),
 (12.37,51.34,45,"16–19/10","Trận các dân tộc",R,"Trận đánh kéo dài bốn ngày, được gọi là Trận các dân tộc. Các đơn vị Saxony đổi phe giữa trận.",[],[],None,(500000,"binh sĩ tham chiến")),
 (12.37,51.34,38,"19/10/1813","Cây cầu",Bl,"Khi Pháp rút, cây cầu duy nhất qua sông Elster bị phá sớm, hàng chục nghìn lính bị kẹt lại. Năm sau, Napoleon thoái vị.",[((12.37,51.34),(11.8,51.2),Bl)],[],(12.33,51.33),None)],
 {"Napoleon":"na pô lê ông","Leipzig":"lai xích","Saxony":"xắc xô ni","Elster":"en xtơ","Phổ":"phổ"}),
topic("borodino_1812","Borodino 1812","","Bạn có biết? Năm 1812, Napoleon thắng ở Borodino, vào được Moskva, nhưng lại mất gần hết đại quân.",[
 (24.0,54.7,10,"6/1812","Vượt sông Niemen",Bl,"Tháng sáu năm 1812, Napoleon dẫn hơn bốn trăm nghìn quân vượt sông Niemen tiến vào nước Nga.",[((23.9,54.9),(32.0,54.8),Bl)],[((23.9,54.9),"Niemen")],None,None),
 (35.8,55.5,30,"7/9/1812","Borodino",O,"Ngày bảy tháng chín, tướng Kutuzov chặn Napoleon ở Borodino. Đây là ngày đẫm máu nhất của các cuộc chiến tranh Napoleon.",[((35.6,55.45),(35.85,55.52),Bl)],[((35.82,55.52),"Borodino")],(35.85,55.52),None),
 (37.6,55.75,28,"9/1812","Moskva",R,"Quân Nga rút lui, Napoleon vào Moskva nhưng thành phố bốc cháy và Nga không chịu cầu hoà.",[((35.8,55.5),(37.6,55.75),Bl)],[((37.62,55.75),"Moskva")],None,None),
 (30.0,55.0,9,"11/1812","Rút lui",R,"Trong mùa đông, đói rét và quân Nga truy kích làm đại quân tan rã. Chỉ một phần nhỏ trở về được.",[((37.6,55.7),(24.0,54.8),Bl)],[],(28.5,54.3),None)],
 {"Napoleon":"na pô lê ông","Borodino":"bo rô đi nô","Niemen":"ni ê men","Kutuzov":"cu tu dốp","Moskva":"mát xcơ va"}),
topic("sedan_1870","Sedan 1870","BME","Bạn có biết? Năm 1870, một hoàng đế Pháp đã bị bắt làm tù binh chỉ sau vài tuần chiến tranh.",[
 (7.0,49.5,18,"7/1870","Chiến tranh",R,"Pháp tuyên chiến với Phổ. Nhưng quân Phổ và đồng minh Đức huy động nhanh hơn nhờ đường sắt.",[((8.5,49.8),(6.5,49.2),R)],[],None,None),
 (6.17,49.12,35,"8/1870","Vây Metz",O,"Một đạo quân Pháp lớn bị vây kín trong pháo đài Metz.",[((6.5,49.3),(6.2,49.15),R)],[((6.17,49.12),"Metz")],None,None),
 (4.94,49.7,50,"1/9/1870","Sedan",R,"Hoàng đế Napoleon đệ Tam đi cùng đạo quân cứu viện, nhưng bị bao vây ở Sedan, pháo Phổ bắn từ các ngọn đồi xung quanh.",[((5.2,49.8),(4.95,49.7),R),((4.7,49.6),(4.93,49.7),R)],[((4.94,49.7),"Sedan")],(4.94,49.7),None),
 (2.35,48.85,18,"1871","Đế chế Đức",G,"Napoleon đệ Tam đầu hàng cùng quân đội. Năm 1871, Đế chế Đức được tuyên bố ngay tại cung điện Versailles.",[((4.9,49.7),(2.4,48.85),R)],[((2.12,48.8),"Versailles")],None,None)],
 {"Phổ":"phổ","Metz":"mét","Sedan":"xơ đăng","Napoleon":"na pô lê ông","Versailles":"véc xai"}),
topic("verdun_1916","Verdun 1916","BME","Bạn có biết? Năm 1916, trận Verdun kéo dài khoảng ba trăm ngày, một trong những trận đánh dài nhất lịch sử.",[
 (5.39,49.16,30,"21/2/1916","Mở màn",R,"Ngày hai mươi mốt tháng hai, quân Đức mở màn bằng trận pháo kích dữ dội vào khu pháo đài Verdun.",[((5.6,49.35),(5.4,49.2),R)],[((5.39,49.16),"Verdun")],None,None),
 (5.44,49.2,50,"2/1916","Douaumont",O,"Pháo đài Douaumont rơi vào tay quân Đức chỉ sau vài ngày. Nước Pháp quyết tâm không để Verdun thất thủ.",[],[((5.44,49.22),"Douaumont")],(5.44,49.22),None),
 (5.2,48.8,28,"1916","Con đường thiêng",G,"Tướng Pétain tổ chức tiếp tế bằng xe tải liên tục trên con đường được gọi là Con đường thiêng.",[((5.16,48.77),(5.38,49.15),Bl)],[((5.16,48.77),"Bar le Duc")],None,None),
 (5.39,49.16,40,"12/1916","Cối xay thịt",R,"Đến cuối năm, Pháp giành lại phần lớn đất đã mất. Hai bên chịu tổng cộng hàng trăm nghìn thương vong.",[((5.4,49.18),(5.45,49.22),Bl)],[],None,None)],
 {"Verdun":"vec đanh","Douaumont":"đu ô mông","Pétain":"pê tanh","Bar":"ba","le":"lơ","Duc":"đúc"}),
topic("kursk_1943","Kursk 1943","","Bạn có biết? Năm 1943, trận xe tăng lớn nhất lịch sử diễn ra quanh thành phố Kursk.",[
 (36.2,51.7,14,"1943","Vòng cung Kursk",O,"Sau Stalingrad, chiến tuyến tạo thành một vòng cung lồi quanh Kursk. Đức định cắt vòng cung này từ hai phía.",[],[((36.19,51.73),"Kursk")],None,None),
 (36.2,51.7,22,"5/7/1943","Thành Trì",R,"Ngày năm tháng bảy, Đức mở chiến dịch Thành Trì. Nhưng Liên Xô đã biết trước, xây hệ thống phòng thủ sâu nhiều lớp.",[((36.0,53.0),(36.1,52.2),R),((36.5,50.6),(36.3,51.2),R)],[],None,None),
 (36.6,51.0,35,"12/7/1943","Prokhorovka",R,"Ngày mười hai tháng bảy, hàng trăm xe tăng hai bên đụng độ gần làng Prokhorovka.",[((37.0,51.1),(36.65,51.03),Bl)],[((36.73,51.04),"Prokhorovka")],(36.7,51.03),None),
 (36.2,51.0,12,"8/1943","Phản công",Bl,"Đức dừng tấn công. Hồng quân phản công, giải phóng Oryol và Kharkov. Từ đây, quyền chủ động ở mặt trận phía đông thuộc về Liên Xô.",[((36.2,51.5),(36.2,50.0),Bl),((36.2,52.0),(36.1,52.95),Bl)],[((36.23,49.99),"Kharkov")],None,None)],
 {"Kursk":"cuốc xcơ","Stalingrad":"xta lin grát","Prokhorovka":"prô khô rốp ca","Oryol":"ô ri ôn","Kharkov":"khác cốp"}),
topic("berlin_1945","Berlin 1945","BME","Bạn có biết? Tháng tư năm 1945, Hồng quân chỉ mất khoảng hai tuần để đánh vào trung tâm Berlin.",[
 (14.6,52.6,30,"16/4/1945","Sông Oder",R,"Ngày mười sáu tháng tư, hàng triệu quân Liên Xô mở cuộc tấn công từ sông Oder.",[((14.6,52.6),(13.6,52.55),R)],[((14.6,52.35),"Oder")],None,(2500000,"quân Liên Xô")),
 (14.3,52.6,40,"4/1945","Seelow",O,"Cao điểm Seelow là tuyến phòng thủ cuối của Đức, chặn quân Zhukov nhiều ngày trước khi bị phá.",[((14.5,52.6),(14.38,52.53),R)],[((14.38,52.53),"Seelow")],(14.38,52.53),None),
 (13.4,52.52,55,"25/4/1945","Bao vây",R,"Các phương diện quân của Zhukov và Konev khép vòng vây Berlin. Cùng ngày, quân Mỹ và Liên Xô gặp nhau trên sông Elbe.",[((13.9,52.7),(13.45,52.55),R),((13.6,52.2),(13.42,52.48),R)],[((13.4,52.52),"Berlin")],None,None),
 (13.38,52.52,55,"2/5/1945","Thất thủ",R,"Ngày ba mươi tháng tư, Hitler tự sát. Ngày hai tháng năm, Berlin đầu hàng. Chưa đầy một tuần sau, chiến tranh ở châu Âu kết thúc.",[],[],(13.38,52.52),None)],
 {"Oder":"ô đơ","Seelow":"xê lô","Zhukov":"giu cốp","Konev":"cô nhép","Elbe":"en bơ","Berlin":"béc lin","Hitler":"hít le"}),
topic("actium_31bc","Actium 31 TCN","","Bạn có biết? Năm 31 TCN, một trận hải chiến ở Hy Lạp đã quyết định ai sẽ làm chủ La Mã.",[
 (20.0,39.0,10,"32 TCN","Nội chiến",R,"Octavian đối đầu Mark Antony và nữ hoàng Ai Cập Cleopatra. Hạm đội Antony đóng ở vịnh Ambracia, phía tây Hy Lạp.",[((29.9,31.2),(20.8,38.95),R)],[((29.9,31.2),"Alexandria")],None,None),
 (20.75,38.95,35,"31 TCN","Phong toả",Bl,"Đô đốc Agrippa của Octavian phong toả, cắt đường tiếp tế. Quân Antony đói và bệnh, nhiều người bỏ trốn.",[((20.5,38.8),(20.7,38.93),Bl)],[((20.73,38.95),"Actium")],None,None),
 (20.6,38.95,40,"2/9/31 TCN","Phá vây",O,"Ngày hai tháng chín, Antony đưa hạm đội ra phá vây. Giữa trận, đội tàu của Cleopatra giương buồm bỏ đi, Antony bám theo.",[((20.7,38.95),(20.5,38.9),R),((20.5,38.9),(21.5,37.5),G)],[],(20.6,38.92),None),
 (29.9,31.2,18,"30 TCN","Ai Cập",G,"Năm sau, Antony và Cleopatra tự sát ở Alexandria. Octavian trở thành Augustus, hoàng đế đầu tiên của La Mã.",[((20.6,38.9),(29.9,31.2),Bl)],[],None,None)],
 {"Octavian":"ốc ta vi an","Mark":"mác","Antony":"an tô ni","Cleopatra":"clê ô pát ra","Ambracia":"am bra xi a","Agrippa":"a gríp pa","Actium":"ắc ti um","Alexandria":"a lếch xan đri a","Augustus":"au gút tút"}),
topic("manzikert_1071","Manzikert 1071","","Bạn có biết? Năm 1071, một hoàng đế Đông La Mã đã bị bắt sống, mở cửa Anatolia cho người Thổ.",[
 (36.0,39.0,10,"1071","Hành quân",Bl,"Hoàng đế Byzantine Romanos đệ Tứ dẫn đại quân về phía đông để chặn người Thổ Seljuk.",[((29.0,41.0),(41.5,39.1),Bl)],[((28.98,41.01),"Constantinople")],None,None),
 (42.5,39.1,30,"1071","Manzikert",O,"Gần pháo đài Manzikert, ông gặp quân của sultan Alp Arslan, chủ yếu là kỵ xạ cơ động.",[((43.2,38.9),(42.6,39.1),R)],[((42.53,39.14),"Manzikert")],None,None),
 (42.5,39.1,38,"26/8/1071","Rối loạn",R,"Kỵ xạ Seljuk giả rút lui, quấy rối liên tục. Khi Romanos ra lệnh lui quân, một bộ phận rút đi sớm khiến đội hình hỗn loạn.",[((42.6,39.2),(42.5,39.1),R)],[],(42.5,39.1),None),
 (33.0,39.0,9,"Sau 1071","Anatolia",R,"Romanos bị bắt sống rồi được thả. Nhưng nội chiến Byzantine sau đó mở đường cho người Thổ tràn vào Anatolia.",[((42.0,39.0),(33.0,39.0),R)],[],None,None)],
 {"Byzantine":"bi dăng tin","Romanos":"rô ma nốt","Seljuk":"xen giúc","Manzikert":"man di kéc","Alp":"anp","Arslan":"ác xlan","Anatolia":"a na tô li a","Constantinople":"công xtăng ti nốp"}),
topic("xich_bich_208","Xích Bích 208","","Bạn có biết? Năm 208, lửa trên sông Trường Giang đã chia Trung Hoa thành thế chân vạc Tam Quốc.",[
 (113.0,32.0,12,"208","Tào Tháo",R,"Tào Tháo đã thống nhất phương bắc, dẫn đại quân xuống nam, chiếm Kinh Châu, định tiêu diệt Tôn Quyền và Lưu Bị.",[((114.0,35.0),(112.2,30.4),R)],[((112.2,30.35),"Giang Lăng")],None,None),
 (113.9,29.9,30,"208","Liên minh",Bl,"Tôn Quyền và Lưu Bị liên minh. Chu Du chỉ huy thuỷ quân Đông Ngô chặn quân Tào trên sông Trường Giang.",[((115.0,29.8),(114.0,29.9),Bl)],[((113.9,29.9),"Xích Bích")],None,None),
 (113.9,29.9,35,"208","Hoả công",O,"Hoàng Cái giả hàng, đưa thuyền chở đầy vật dễ cháy áp sát rồi phóng hoả. Gió thổi lửa lan vào thuyền và doanh trại quân Tào.",[((114.1,29.85),(113.9,29.9),O)],[],(113.88,29.9),None),
 (112.0,30.0,14,"Sau 208","Tam Quốc",G,"Bệnh dịch cùng thất bại buộc Tào Tháo rút về bắc. Thế chân vạc Nguỵ, Thục, Ngô dần hình thành.",[((113.9,29.9),(113.5,32.0),R)],[],None,None)]),
topic("talas_751","Talas 751","","Bạn có biết? Năm 751, nhà Đường và nhà Abbasid đã đụng độ ở Trung Á, trận đánh duy nhất giữa hai đế chế này.",[
 (75.0,40.0,8,"751","Hai đế chế",O,"Nhà Đường mở rộng ảnh hưởng sang Trung Á, còn triều Abbasid vừa lên nắm quyền thế giới Hồi giáo.",[((80.0,41.0),(73.0,42.5),R),((64.0,39.0),(71.0,42.5),G)],[],None,None),
 (72.3,42.5,30,"751","Sông Talas",R,"Tướng Cao Tiên Chi dẫn quân Đường tiến tới sông Talas, đối đầu quân Abbasid của Ziyad ibn Salih.",[((73.0,42.6),(72.4,42.5),R)],[((72.3,42.5),"Talas")],None,None),
 (72.3,42.5,36,"751","Đổi phe",G,"Sau nhiều ngày giao chiến, lính Karluk trong đội hình Đường đổi phe, đánh từ phía sau. Quân Đường thua lớn.",[((72.5,42.8),(72.3,42.5),G)],[],(72.3,42.5),None),
 (68.0,40.0,10,"Sau 751","Giấy",Bl,"Theo truyền thuyết phổ biến, tù binh Đường đã truyền nghề làm giấy đến Samarkand. Nhà Đường cũng sớm suy yếu vì loạn An Sử.",[((72.3,42.5),(66.96,39.65),O)],[((66.96,39.65),"Samarkand")],None,None)],
 {"Abbasid":"áp ba xít","Talas":"ta lát","Ziyad":"di dát","ibn":"íp","Salih":"xa lích","Karluk":"các lúc","Samarkand":"xa mác can"}),
topic("tsushima_1905","Tsushima 1905","","Bạn có biết? Năm 1905, hạm đội Nga đi nửa vòng trái đất chỉ để bị tiêu diệt trong hai ngày.",[
 (40.0,30.0,3.5,"10/1904","Nửa vòng trái đất",R,"Trong chiến tranh Nga Nhật, hạm đội Baltic của Nga rời châu Âu, đi khoảng ba mươi nghìn cây số sang Viễn Đông.",[((20.0,55.0),(18.0,0.0),R),((40.0,-30.0),(109.0,12.0),R)],[],None,(30000,"km hải trình")),
 (109.2,12.2,25,"1905","Cam Ranh",O,"Trên đường, hạm đội dừng chân ở vịnh Cam Ranh của Đông Dương thuộc Pháp trước khi đi về phía bắc.",[],[((109.2,11.95),"Cam Ranh")],None,None),
 (129.5,34.3,25,"27/5/1905","Eo Tsushima",Bl,"Ngày hai mươi bảy tháng năm, đô đốc Tōgō chặn đầu ở eo biển Tsushima, tập trung hoả lực vào các tàu dẫn đầu.",[((130.2,34.0),(129.6,34.3),Bl),((128.5,33.5),(129.4,34.2),R)],[((129.3,34.4),"Tsushima")],(129.5,34.3),None),
 (130.0,35.0,15,"1905","Kết thúc",G,"Hầu hết thiết giáp hạm Nga bị đánh chìm hoặc bị bắt. Nga phải cầu hoà, châu Á chứng kiến một cường quốc châu Âu thua trên biển.",[],[],None,None)],
 {"Baltic":"ban tích","Tsushima":"chư si ma","Tōgō":"tô gô"},True),
topic("plassey_1757","Plassey 1757","","Bạn có biết? Năm 1757, một trận đánh ngắn ở Bengal đã mở đường cho Anh cai trị Ấn Độ.",[
 (88.3,22.6,25,"1756","Calcutta",R,"Nawab xứ Bengal là Siraj ud Daulah chiếm Calcutta của Công ty Đông Ấn Anh.",[((88.2,24.2),(88.35,22.6),R)],[((88.36,22.57),"Calcutta")],None,None),
 (88.3,23.5,25,"1757","Âm mưu",Bl,"Robert Clive dẫn quân tái chiếm, rồi bí mật thoả thuận với Mir Jafar, chỉ huy quân của nawab.",[((88.36,22.6),(88.25,23.75),Bl)],[],None,None),
 (88.25,23.8,40,"23/6/1757","Plassey",O,"Ngày hai mươi ba tháng sáu, ở Plassey, mưa làm ướt thuốc súng phía nawab. Mir Jafar án binh bất động.",[((88.3,23.85),(88.26,23.79),R)],[((88.25,23.8),"Plassey")],(88.26,23.8),None),
 (85.0,24.0,10,"Sau 1757","Công ty Đông Ấn",G,"Siraj thua và bị giết, Mir Jafar lên ngôi dưới sự bảo trợ của Anh. Từ Bengal, Công ty Đông Ấn dần mở rộng quyền lực khắp Ấn Độ.",[((88.2,23.8),(80.0,25.0),Bl)],[],None,None)],
 {"Bengal":"ben gan","Nawab":"na váp","nawab":"na váp","Siraj":"xi rát","ud":"út","Daulah":"đau la","Calcutta":"can cút ta","Robert":"rô bớt","Clive":"clai","Mir":"mia","Jafar":"gia pha","Plassey":"pla xi"}),
topic("panipat_1526","Panipat 1526","","Bạn có biết? Năm 1526, đại bác và kỵ xạ đã giúp Babur lập nên Đế quốc Mughal ở Ấn Độ.",[
 (69.2,34.5,14,"1526","Kabul",G,"Babur, hậu duệ của Timur và Thành Cát Tư Hãn, từ Kabul tiến xuống đồng bằng Ấn Độ.",[((69.2,34.5),(76.0,29.5),G)],[((69.2,34.53),"Kabul")],None,None),
 (76.97,29.39,30,"21/4/1526","Panipat",O,"Tại Panipat, khoảng mười hai nghìn quân của Babur đối đầu đại quân đông hơn nhiều của sultan Ibrahim Lodi, kèm cả voi chiến.",[((77.1,29.45),(77.0,29.4),R)],[((76.97,29.39),"Panipat")],None,None),
 (76.97,29.39,40,"1526","Đại bác",R,"Babur dùng xe nối xích làm tường chắn, đặt đại bác và súng phía sau, kỵ xạ đánh vòng hai cánh. Voi chiến hoảng loạn.",[((76.9,29.45),(77.0,29.38),G),((76.9,29.33),(77.0,29.4),G)],[],(77.0,29.4),None),
 (77.2,28.6,25,"1526","Mughal",G,"Ibrahim Lodi tử trận. Babur vào Delhi và Agra, mở đầu Đế quốc Mughal tồn tại hơn ba thế kỷ.",[((77.0,29.4),(77.2,28.6),G)],[((77.2,28.61),"Delhi")],None,None)],
 {"Babur":"ba bua","Mughal":"mô gồn","Timur":"ti mua","Kabul":"ca bun","Panipat":"pa ni pát","Ibrahim":"i bra him","Lodi":"lô đi","Delhi":"đê li","Agra":"a gra"}),
topic("saratoga_1777","Saratoga 1777","","Bạn có biết? Năm 1777, một đạo quân Anh đầu hàng ở Saratoga, khiến Pháp quyết định đứng về phía nước Mỹ non trẻ.",[
 (-73.5,44.5,18,"6/1777","Từ Canada",R,"Tướng Anh John Burgoyne từ Canada tiến xuống dọc hồ Champlain, định cắt rời vùng New England.",[((-73.4,45.5),(-73.6,43.2),R)],[((-73.4,44.5),"Champlain")],None,None),
 (-73.6,43.0,30,"8/1777","Bị kéo dài",O,"Đường xa, rừng rậm và quân Mỹ phá đường làm quân Anh di chuyển chậm và thiếu tiếp tế.",[],[((-73.62,43.01),"Saratoga")],None,None),
 (-73.62,43.0,45,"9–10/1777","Saratoga",Bl,"Hai trận đánh quanh Saratoga, quân Mỹ của tướng Horatio Gates cùng Benedict Arnold chặn đứng quân Anh.",[((-73.65,42.95),(-73.62,43.0),Bl)],[],(-73.62,43.0),None),
 (-40.0,45.0,4,"1778","Liên minh Pháp",G,"Ngày mười bảy tháng mười, Burgoyne đầu hàng. Năm sau, Pháp ký liên minh với Mỹ, thay đổi cục diện cuộc chiến giành độc lập.",[((2.3,48.8),(-70.0,41.0),Bl)],[],None,None)],
 {"John":"giôn","Burgoyne":"bơ goi","Canada":"ca na đa","Champlain":"sam plên","New":"niu","England":"ing lừn","Saratoga":"xa ra tô ga","Horatio":"hô rây si ô","Gates":"ghết","Benedict":"be nơ đích","Arnold":"a nôn"}),
topic("tenochtitlan_1521","Tenochtitlan 1521","","Bạn có biết? Năm 1521, kinh đô Aztec trên hồ, một trong những thành phố lớn nhất thế giới, đã thất thủ.",[
 (-96.1,19.2,20,"1519","Đổ bộ",R,"Hernán Cortés đổ bộ lên Veracruz với vài trăm lính Tây Ban Nha và kết đồng minh với người Tlaxcala, kẻ thù của Aztec.",[((-96.1,19.2),(-98.2,19.3),R)],[((-96.13,19.18),"Veracruz")],None,None),
 (-99.13,19.43,35,"1520","Đêm u sầu",O,"Năm 1520, người Tây Ban Nha bị đánh bật khỏi Tenochtitlan trong một đêm rút chạy đẫm máu.",[((-99.13,19.43),(-98.5,19.4),R)],[((-99.13,19.43),"Tenochtitlan")],None,None),
 (-99.1,19.4,45,"1521","Vây hồ",R,"Cortés quay lại với hàng chục nghìn chiến binh bản địa đồng minh, đóng thuyền chiến trên hồ để phong toả kinh đô.",[((-98.9,19.5),(-99.08,19.44),R),((-99.0,19.3),(-99.1,19.4),R)],[],None,None),
 (-99.13,19.43,40,"13/8/1521","Thất thủ",G,"Dịch đậu mùa và đói khát tàn phá thành phố. Ngày mười ba tháng tám năm 1521, Tenochtitlan thất thủ. Thành phố Mexico ngày nay mọc lên trên nền cũ.",[],[],(-99.13,19.43),None)],
 {"Aztec":"át téc","Hernán":"ec nan","Cortés":"cóc tét","Veracruz":"vê ra crút","Tlaxcala":"tla xca la","Tenochtitlan":"tê nốt ti tlan","Mexico":"mê hi cô"}),
topic("pearl_harbor_1941","Trân Châu Cảng 1941","","Bạn có biết? Sáng bảy tháng mười hai năm 1941, máy bay Nhật bất ngờ tấn công Trân Châu Cảng, kéo Mỹ vào Thế chiến hai.",[
 (-172.0,30.0,6,"26/11/1941","Hạm đội Nhật",R,"Hạm đội tàu sân bay Nhật bí mật rời quần đảo Kuril, vượt Thái Bình Dương trong im lặng vô tuyến.",[((-178.0,33.0),(-159.0,23.0),R)],[],None,(6,"tàu sân bay")),
 (-158.0,21.4,40,"7/12/1941","Đợt một",O,"Sáng chủ nhật, đợt máy bay đầu tiên ập xuống Trân Châu Cảng trên đảo Oahu, Hawaii.",[((-158.2,22.0),(-157.95,21.37),R)],[((-157.95,21.36),"Trân Châu Cảng")],None,None),
 (-157.95,21.36,60,"7/12/1941","Arizona",R,"Thiết giáp hạm Arizona nổ tung, hơn một nghìn thuỷ thủ trên tàu thiệt mạng. Tổng cộng hơn hai nghìn bốn trăm người Mỹ chết.",[],[],(-157.95,21.36),None),
 (-158.0,21.4,25,"8/12/1941","Tuyên chiến",Bl,"Nhưng các tàu sân bay Mỹ không có mặt trong cảng. Ngày hôm sau, Mỹ tuyên chiến với Nhật.",[],[],None,None)],
 {"Kuril":"cu rin","Oahu":"ô a hu","Hawaii":"ha oai","Arizona":"a ri dô na"}),
topic("kadesh_1274bc","Kadesh 1274 TCN","","Bạn có biết? Khoảng năm 1274 TCN, Ai Cập và người Hittite đánh trận xe chiến mã lớn nhất từng được ghi chép.",[
 (34.0,32.0,10,"1274 TCN","Hành quân",G,"Pharaoh Ramesses đệ Nhị dẫn quân Ai Cập lên phía bắc, tranh giành vùng Syria với đế quốc Hittite.",[((31.0,30.5),(36.4,34.4),G)],[((36.51,34.56),"Kadesh")],None,None),
 (36.51,34.56,35,"1274 TCN","Tin giả",O,"Hai do thám bị bắt nói rằng quân Hittite còn ở xa. Ramesses tin và tiến lên trước với một phần quân.",[((36.4,34.3),(36.5,34.5),G)],[],None,None),
 (36.51,34.56,40,"1274 TCN","Xe chiến mã",R,"Hàng nghìn xe chiến mã Hittite của vua Muwatalli bất ngờ đánh vào đội quân đang hành quân của Ai Cập.",[((36.6,34.6),(36.5,34.5),R)],[],(36.5,34.52),None),
 (35.0,33.5,12,"1259 TCN","Hoà ước",Bl,"Ramesses cầm cự đến khi viện binh tới. Không bên nào thắng hẳn. Vài chục năm sau, hai bên ký một trong những hoà ước sớm nhất còn lưu lại.",[],[],None,None)],
 {"Hittite":"hít tai","Pharaoh":"pha ra ông","Ramesses":"ram xét","Syria":"xi ri","Kadesh":"ca đét","Muwatalli":"mu va ta li"}),
topic("ung_chau_1075","Lý Thường Kiệt đánh Ung Châu 1075","BMV","Bạn có biết? Năm 1075, Đại Việt đã chủ động đánh sang đất Tống để phá thế xâm lược từ gốc.",[
 (106.5,22.0,18,"1075","Nhà Tống",R,"Nhà Tống chuẩn bị binh lực và lương thảo ở vùng biên giới để đánh Đại Việt.",[],[((108.3,22.8),"Ung Châu")],None,None),
 (108.0,22.0,25,"1075","Tiên phát chế nhân",G,"Lý Thường Kiệt chủ trương tiên phát chế nhân, đem quân thuỷ bộ đánh vào Khâm Châu, Liêm Châu rồi tiến về Ung Châu.",[((106.7,21.6),(108.6,21.95),G),((106.7,22.3),(108.0,22.7),G)],[((108.62,21.95),"Khâm Châu")],None,None),
 (108.3,22.8,40,"1076","Ung Châu",O,"Thành Ung Châu bị vây hơn bốn mươi ngày rồi bị hạ. Kho lương và căn cứ chuẩn bị xâm lược bị phá.",[((108.1,22.7),(108.3,22.8),G)],[],(108.3,22.8),None),
 (106.5,21.2,20,"1077","Như Nguyệt",Bl,"Đại Việt rút quân về chủ động phòng thủ. Năm sau, quân Tống tràn sang và bị chặn lại ở phòng tuyến sông Như Nguyệt.",[((108.3,22.8),(106.3,21.4),G)],[],None,None)],
 {},True),
topic("dong_bo_dau_1258","Đông Bộ Đầu 1258","BMV","Bạn có biết? Năm 1258, quân Mông Cổ vào được Thăng Long nhưng chỉ ít ngày sau đã bị đánh bật ra.",[
 (104.5,22.5,18,"1/1258","Mông Cổ tràn xuống",R,"Tướng Mông Cổ Ngột Lương Hợp Thai từ Vân Nam tiến xuống Đại Việt theo lưu vực sông Thao.",[((103.5,23.5),(105.4,21.3),R)],[],None,None),
 (105.5,21.3,30,"1258","Bình Lệ Nguyên",O,"Vua Trần Thái Tông chặn giặc ở Bình Lệ Nguyên rồi rút lui để bảo toàn lực lượng, để lại Thăng Long trống.",[((105.6,21.3),(105.85,21.03),G)],[((105.6,21.3),"Bình Lệ Nguyên")],None,None),
 (105.85,21.04,45,"1258","Thăng Long trống",R,"Quân Mông Cổ vào Thăng Long nhưng thiếu lương, không quen thuỷ thổ, rơi vào thế bị động.",[((105.6,21.3),(105.84,21.04),R)],[((105.84,21.03),"Thăng Long")],None,None),
 (105.85,21.05,45,"1258","Đông Bộ Đầu",G,"Quân Trần phản công ở Đông Bộ Đầu bên sông Hồng. Quân Mông Cổ thua chạy về Vân Nam, kết thúc cuộc xâm lược lần thứ nhất.",[((105.95,20.95),(105.86,21.05),G),((105.86,21.05),(104.0,22.8),R)],[((105.86,21.05),"Đông Bộ Đầu")],(105.85,21.05),None)],
 {},True),
topic("bien_gioi_1950","Chiến dịch Biên giới 1950","BMV","Bạn có biết? Năm 1950, chiến thắng Đông Khê đã khai thông biên giới Việt Trung trên Đường số bốn.",[
 (106.5,22.2,22,"1950","Đường số 4",R,"Quân Pháp lập một chuỗi đồn dọc Đường số bốn từ Cao Bằng đến Lạng Sơn, phong toả biên giới.",[],[((106.26,22.67),"Cao Bằng"),((106.76,21.85),"Lạng Sơn")],None,None),
 (106.42,22.43,45,"16/9/1950","Đông Khê",O,"Ngày mười sáu tháng chín, quân ta nổ súng đánh cứ điểm Đông Khê. Sau hơn hai ngày chiến đấu, Đông Khê bị tiêu diệt.",[((106.5,22.5),(106.43,22.43),G)],[((106.43,22.43),"Đông Khê")],(106.43,22.43),None),
 (106.4,22.4,35,"10/1950","Lepage và Charton",R,"Pháp cho binh đoàn Lepage lên đón binh đoàn Charton rút khỏi Cao Bằng. Cả hai bị chặn đánh trên vùng núi Cốc Xá.",[((106.6,22.2),(106.45,22.4),R),((106.26,22.67),(106.4,22.48),R)],[],(106.42,22.45),None),
 (106.5,22.1,22,"10/1950","Giải phóng",G,"Quân Pháp lần lượt rút khỏi các đồn dọc Đường số bốn. Biên giới được khai thông, thế trận kháng chiến thay đổi.",[],[],None,None)],
 {"Lepage":"lơ pát","Charton":"sác tông"},True),
]
SKIP={"tours_732"}  # Poitiers 732 already produced
existing={json.load(open(f"{WD}/topics/{f}")).get("title","") for f in (os.listdir(f"{WD}/topics") if os.path.isdir(f"{WD}/topics") else []) if f.endswith(".json")}
os.makedirs(Q,exist_ok=True); n=0
for i,(slug,T) in enumerate(TOP):
    if T["title"] in DONE or T["title"] in existing or slug in SKIP: print("skip dup",slug); continue
    tmp=f"{Q}/.{slug}.tmp"; json.dump(T,open(tmp,"w"),ensure_ascii=False,indent=1); os.rename(tmp,f"{Q}/{i+1:03d}_{slug}.json"); n+=1
    print(f"{i+1:03d}_{slug}: {T['_words']} words")
print(n,"queued")
