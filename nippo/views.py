from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import Koban,nippo
import pandas as pd
from datetime import datetime, timedelta
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.contrib import messages  # メッセージフレームワークをインポート


# Create your views here.

def koban(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        construction_number = request.POST.get('construction_number', '').strip()

        if name and construction_number:
            try:
                koban_entry = Koban.objects.get(name=name)
                # Check if the construction number already exists
                existing_numbers = [
                    koban_entry.koban1, koban_entry.koban2, koban_entry.koban3,
                    koban_entry.koban4, koban_entry.koban5, koban_entry.koban6,
                    koban_entry.koban7, koban_entry.koban8, koban_entry.koban9,
                    koban_entry.koban10
                ]
                if construction_number in existing_numbers:
                    # Duplicate found; do not assign
                    return redirect('koban_update')

                # Find the first available koban field
                for i in range(1, 11):
                    field_name = f'koban{i}'
                    if not getattr(koban_entry, field_name):
                        setattr(koban_entry, field_name, construction_number)
                        koban_entry.save()
                        break
                # If all fields are filled, do nothing
            except Koban.DoesNotExist:
                # Create a new Koban entry with koban1
                Koban.objects.create(name=name, koban1=construction_number)

        # Redirect to the same page after processing
        return redirect('koban_update')

    return render(request, 'nippo/koban.html')

def delete_Koban(request):
    if request.method == 'POST':
        # busnumber以外のデータを削除
        Koban.objects.update(
            koban1='',
            koban2='',
            koban3='',
            koban4='',
            koban5='',
            koban6='',
            koban7='',
            koban8='',
            koban9='',
            koban10='',
        )
    return redirect('koban_update')


def approval(request):
    # データベースからすべてのNippoデータを取得
    nippo_records = nippo.objects.all()
    return render(request, 'nippo/approval.html', {'nippo_records': nippo_records})

def update_status(request):
    if request.method == 'POST':
        # フォームで送信された選択された行のidxを取得
        selected_rows = request.POST.getlist('selected_rows')
        
        # 選択されたidxのデータを更新
        nippo.objects.filter(idx__in=selected_rows).update(status=1)
        
        # 一覧画面にリダイレクト
        return redirect('napproval')
    return HttpResponse("Invalid request method.", status=400)


def nippologin(request):
    if request.method == 'POST':
        if 'name' in request.POST and 'job_submit' not in request.POST:
            # 名前が入力された場合、関連する交番を取得してフォームを表示
            name = request.POST.get('name').strip()
            request.session['name'] = name  # nameをセッションに保存
            if name in ["2021m116","2021m092"]:
                trans_option=1   
            else:
                trans_option=0
            request.session['trans_option'] = trans_option  # nameをセッションに保存



            try:
                koban_entry = Koban.objects.get(name=name)
                koban_numbers = []
                for i in range(1, 11):
                    field_name = f'koban{i}'
                    value = getattr(koban_entry, field_name)
                    if value:
                        koban_numbers.append({'field': field_name, 'value': value})
                                # koban_numbersもセッションに保存する場合
                request.session['koban_numbers'] = koban_numbers

                # nippohomeにリダイレクトする
                return redirect('nhome')
            
            except Koban.DoesNotExist:
                # 名前が存在しない場合、再度名前入力フォームを表示
                return redirect('nlogin')
    else:
        # GETリクエストの場合、名前入力フォームを表示
        return render(request, 'nippo/nlogin.html')

# 通常日報入力*****************************************************
def nippohome(request):
    if 'action' in request.POST:
            # 勤怠情報*****************************************************
            #print(request.POST)  
            name = request.session.get('name')  
            koban_numbers = request.session.get('koban_numbers')
            time_format = "%H:%M"
            date = request.POST.get('content')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            koban0 = request.POST.get('koban0')
            trans = request.POST.get('trans') 
            trans_office = request.POST.get('trans_office')            
            break_time_start1 = request.POST.get('break_time_start1')
            break_time_end1 = request.POST.get('break_time_end1')
            break_time_none = request.POST.get('break_time_none')      

            # 特殊入力*****************************************************
            break_time_start2 = request.POST.get('break_time_start2')
            break_time_end2 = request.POST.get('break_time_end2')
            lunch_box = request.POST.get('lunch_box')  
            comment = request.POST.get('comment')


            # 計算ロジック(休憩)*****************************************************         
            if break_time_start1 and break_time_end1:
                break_time_start1_d = datetime.strptime(break_time_start1, time_format)
                break_time_end1_d = datetime.strptime(break_time_end1, time_format)
                break_time_duration1_d = break_time_end1_d - break_time_start1_d
            else:
                break_time_duration1_d = timedelta(0)

            if break_time_start2 and break_time_end2:
                break_time_start2_d = datetime.strptime(break_time_start2, time_format)
                break_time_end2_d = datetime.strptime(break_time_end2, time_format)
                break_time_duration2_d = break_time_end2_d - break_time_start2_d
            else:
                break_time_duration2_d = timedelta(0) 
    
            total_break_time = break_time_duration1_d + break_time_duration2_d  # timedelta

            if break_time_start1 and break_time_end1:
                break_time_start1_t = datetime.strptime(break_time_start1, time_format).time()
                break_time_end1_t = datetime.strptime(break_time_end1, time_format).time()
            else:
                break_time_start1_t = None
                break_time_end1_t = None

            if break_time_start2 and break_time_end2:
                break_time_start2_t = datetime.strptime(break_time_start2, time_format).time()
                break_time_end2_t = datetime.strptime(break_time_end2, time_format).time()
            else:
                break_time_start2_t = None
                break_time_end2_t = None


            # 計算ロジック(勤務時間)*****************************************************
            start_time_d = datetime.strptime(start_time, time_format)
            end_time_d = datetime.strptime(end_time, time_format)
            total_time =end_time_d-start_time_d-total_break_time
            total_time_kinmu_t=end_time_d-start_time_d
            
            if total_time_kinmu_t.days < 0:
                total_time_kinmu_t = timedelta(seconds=total_time_kinmu_t.seconds) 
            if total_time.days < 0:
                total_time = timedelta(seconds=total_time.seconds)  
 

            eight_hours = timedelta(hours=8)
            zangyo=total_time-eight_hours

            start_time_t = datetime.strptime(start_time,time_format).time()
            end_time_t = datetime.strptime(end_time, time_format).time()

            if zangyo < timedelta(0):
                zangyo = timedelta(0)


            # タイムスタンプ・idx生成*****************************************************
            current_time =(datetime.utcnow() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")

            qs = nippo.objects.all().values('idx')
            if not qs:
                new_idx=1
            else:
                df = pd.DataFrame.from_records(qs)
                df['idx'] = df['idx'].fillna(0).astype(str).str.split('-').str[0]
                df['idx'] = df['idx'].astype(int)
                max_prefix = df['idx'].max()
                new_prefix = max_prefix + 1
                new_idx = str(new_prefix)
                print(new_idx)


            # 送信*****************************************************
            try:
                with transaction.atomic():  
                    sagyo = nippo(
                    idx=new_idx,
                    userid=name,
                    date=date,
                    start=start_time_t,
                    end=end_time_t,
                    break_start=break_time_start1_t,
                    break_end=break_time_end1_t,
                    zangyo=zangyo,
                    total_time=total_time,
                    total_kinmu=total_time_kinmu_t,
                    total_break=total_break_time,
                    koban=koban0,
                    trans=trans,
                    trans_office=trans_office,
                    status=0,
                    sequence=0,
                    add_time=current_time,
                    lunch=lunch_box,
                    comment=comment
                        )
                    sagyo.save()

                    request.session["data_list"] = [
                    {
                    "userid": name,
                    "date": date,
                    "start": start_time_t.strftime('%H:%M:%S'),
                    "end": end_time_t.strftime('%H:%M:%S'),
                    "break_start": break_time_start1_t.strftime('%H:%M:%S') if break_time_start1_t else "",
                    "break_end": break_time_end1_t.strftime('%H:%M:%S') if break_time_end1_t else "",
                    "koban": koban0,
                    "trans": trans,
                    "trans_office": trans_office,
                    'lunch' : lunch_box,
                    'comment':comment

                }
            ]   
            except Exception as e:

                return redirect('nerror')
            
            return redirect('nsuccess')

    else:

            name = request.session.get('name')
            trans_option = request.session.get('trans_option')
            koban_numbers = request.session.get('koban_numbers')
            return render(request, 'nippo/nhome.html', {'name': name, 'koban_numbers': koban_numbers,'trans_option':trans_option})



def nippomultiple(request):# 日報複数入力
    if 'action' in request.POST:
            #print(request.POST)  
            total_break_time = timedelta(0)
            break_time_duration_d=timedelta(0)
            name = request.session.get('name')
            koban_numbers = request.session.get('koban_numbers')
            time_format = "%H:%M"

            date = request.POST.get('content')
            trans = request.POST.get('trans') 
            trans_office = request.POST.get('trans_office')
            break_overlap_flag = request.POST.get('break_overlap_flag', '0')


            break_time_start = request.POST.get('break_time_start')
            break_time_end = request.POST.get('break_time_end')


            lunch_box = request.POST.get('lunch_box')  
            comment = request.POST.get('comment')
            
            if break_time_start and break_time_end:
                break_time_start_d = datetime.strptime(break_time_start, time_format)
                break_time_end_d = datetime.strptime(break_time_end, time_format)
                break_time_duration_d = break_time_end_d - break_time_start_d
                total_break_time = str(break_time_duration_d)
            

            if break_time_start and break_time_end:
                break_time_start_t = datetime.strptime(break_time_start, time_format).time()
                break_time_end_t = datetime.strptime(break_time_end, time_format).time()
            else:
                break_time_start_t = None
                break_time_end_t = None
            
            total_work_time_d_m_sum = timedelta()
            current_time = (datetime.utcnow() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")
            koban_fields = []
            new_prefix = None
# 投稿されたすべてのフォームデータから「koban」「start_time」「end_time」を収集
            for key in request.POST:
                if key.startswith('sequence'):
                    index = key[8:]  # 'sequence'の後ろの数字部分を取得
                    sequence = request.POST.get(f'sequence{index}')
                    koban = request.POST.get(f'koban{index}')
                    start_time = request.POST.get(f'start_time{index}')
                    end_time = request.POST.get(f'end_time{index}')
                    start_time_d = datetime.strptime(start_time, time_format)
                    end_time_d = datetime.strptime(end_time, time_format)

                    start_time = datetime.strptime(start_time,time_format).time()
                    end_time = datetime.strptime(end_time, time_format).time()

                    

                    
                    total_work_time_d_m =end_time_d-start_time_d
                    total_work_time_d_m_sum += total_work_time_d_m

                    total_kinmu_time=end_time_d-start_time_d

                    if total_kinmu_time.days < 0:
                        total_kinmu_time = timedelta(seconds=total_kinmu_time.seconds)  # 負の「日」をリセット
                    if total_work_time_d_m.days < 0:
                        total_work_time_d_m = timedelta(seconds=total_work_time_d_m.seconds)  # 負の「日」をリセット
                    

                    if new_prefix is None:
                        qs = nippo.objects.all().values('idx')
                        if not qs:
                            new_prefix=1
                            new_idx = str(new_prefix)+"-"+str(sequence)
                        else:
            
                            df = pd.DataFrame.from_records(qs)
                            df['idx'] = df['idx'].fillna(0).astype(str).str.split('-').str[0]
                            df['idx'] = df['idx'].astype(int)
                            max_prefix = df['idx'].max()
                            new_prefix = max_prefix + 1
                            new_idx = str(new_prefix)+"-"+str(sequence)
                    else:
                        new_idx = str(new_prefix)+"-"+str(sequence)

        # データを収集
                    koban_fields.append({
                        'idx': new_idx,
                        'userid' : name,
                        'sequence': sequence,
                        'date' : date,
                        'koban': koban,
                        'start': start_time,
                        'end': end_time,
                        'trans' : trans,
                        'trans_office' : trans_office,
                        'break_start' : break_time_start_t,
                        'break_end' : break_time_end_t,
                        'total_break':total_break_time,
                        'status' : 0,
                        'add_time' : current_time,
                        'lunch':lunch_box,
                        'comment':comment
                    })

            #total_work_time_d_m_sum = total_work_time_d_m_sum
            if total_work_time_d_m_sum.days < 0:
               total_work_time_d_m_sum = timedelta(seconds=total_work_time_d_m_sum.seconds) 

            
            if break_overlap_flag=="1":
                total_work_time_d_m_sum = total_work_time_d_m_sum-break_time_duration_d
            else:    
                total_work_time_d_m_sum = total_work_time_d_m_sum
            
            total_work_time = str( total_work_time_d_m_sum)

            eight_hours_d = timedelta(hours=8)

            if break_overlap_flag=="1":
                total_kinmu_time = total_work_time_d_m_sum+break_time_duration_d
            else:    
                total_kinmu_time = total_work_time_d_m_sum+break_time_duration_d  
            
            
            if total_kinmu_time.days < 0:
               total_kinmu_time = timedelta(seconds=total_kinmu_time.seconds)             
            total_kinmu_time = str(total_kinmu_time).zfill(8)


            if break_overlap_flag=="1":
                zangyo = total_work_time_d_m_sum - eight_hours_d
            else:    
                zangyo = total_work_time_d_m_sum - eight_hours_d  


            if zangyo < timedelta(0):
                zangyo = timedelta(0)

            zangyo = str(zangyo)


            for field in koban_fields:
                field['total_time'] = total_work_time
                field['zangyo'] = zangyo
                field['total_kinmu'] = total_kinmu_time
            print(koban_fields)

            for field in koban_fields:
                sagyo = nippo(**field)  # 辞書を展開して渡す
                sagyo.save()

            return redirect('nsuccess_multiple')



    else:

            name = request.session.get('name')  # セッションからnameを取得
            trans_option = request.session.get('trans_option')
            koban_numbers = request.session.get('koban_numbers')  # セッションからkoban_numbersを取得   
            return render(request, 'nippo/nmultiple.html', {'name': name, 'koban_numbers': koban_numbers,'trans_option':trans_option})


def nippohistory(request):# 履歴
    name = request.session.get('name')  # セッションからnameを取得
    if request.method == 'POST':
        selected_month = request.POST.get('selected_month')
        year_month_str = selected_month  # "2024-11" のような文字列

    # dateフィールドが年と月に対応する文字列で始まっているレコードにフィルタ
        sagyo_queryset = nippo.objects.filter(
            userid=name,
            date__startswith=year_month_str
        ).order_by('-date')


    else:
        sagyo_queryset = nippo.objects.filter(userid=name).order_by('-date')[:20]
        sagyo_queryset = sorted(sagyo_queryset, key=lambda x:int(str(x.idx).split('-')[0]),reverse=True)
        year_month_str=""
    
    total_count = nippo.objects.filter(userid=name).count()

    total_kinmu_values = nippo.objects.filter(userid=name, sequence__in=[0, 1]).values_list('total_kinmu', flat=True)


    # 合計時間を計算
    total_time = timedelta(0)  # 初期値を0に設定
    for time_str in total_kinmu_values:
        if time_str:  # Noneでない場合
            # time_strを分割してtimedeltaに変換
            hours, minutes, seconds = map(int, time_str.split(':'))
            total_time += timedelta(hours=hours, minutes=minutes, seconds=seconds)


    # 時間と分に分ける
    total_hours, remainder = divmod(total_time.total_seconds(), 3600)
    total_minutes = remainder // 60

    total_count_status_0 = nippo.objects.filter(userid=name, status=0).count()


# 現在の日付を取得
    #today = datetime.now()
    # 日本時間を取得
    today = datetime.utcnow() + timedelta(hours=9)

# 今日が何曜日かを取得（0:月曜, 6:日曜）
    weekday = today.weekday()


# 直近の月曜日と日曜日の日付を計算
    start_of_week = today - timedelta(days=weekday)  # 直近の月曜日
    end_of_week = start_of_week + timedelta(days=6)  # 直近の月曜日から6日後（同じ週の日曜日）
    # 日付部分だけをフォーマット
    start_of_week_str = start_of_week.strftime('%Y-%m-%d')
    end_of_week_str = end_of_week.strftime('%Y-%m-%d')

# 一週間の勤務時間を取得
    total_kinmu_values_week = nippo.objects.filter(userid=name,date__gte=start_of_week_str,date__lte=end_of_week_str,sequence__in=[0, 1]).values_list('total_kinmu', flat=True)

    #total_time_values_week = nippo.objects.filter(userid=name, date__range=[start_of_week, end_of_week]).values_list('total_time', flat=True)
    #total_time_values_week = nippo.objects.filter(userid=name, date__gte=start_of_week,date__lte=end_of_week ).values_list('total_time', flat=True)

# 合計時間を計算
    total_time_week = timedelta(0)  # 初期値を0に設定
    for time_str in total_kinmu_values_week:
        if time_str:  # Noneでない場合
        # time_strを分割してtimedeltaに変換
            hours_week, minutes_week, seconds_week = map(int, time_str.split(':'))
            total_time_week += timedelta(hours=hours_week, minutes=minutes_week, seconds=seconds_week)

# 時間と分に分ける
    total_hours_week, remainder = divmod(total_time_week.total_seconds(), 3600)
    total_minutes_week = remainder // 60


    # 日本語の曜日リスト（月曜日=0, 日曜日=6）
    weekdays = ['月', '火', '水', '木', '金', '土', '日']
    
    # 各エントリにformatted_date, formatted_start, formatted_endを追加
    sagyo_entries = []
    for entry in sagyo_queryset:
        # 日付の処理
        date = entry.date  # dateが文字列か datetime オブジェクトか確認
        
        if isinstance(date, str):
            try:
                # 文字列を datetime オブジェクトに変換（フォーマットを確認）
                date_obj = datetime.strptime(date, '%Y-%m-%d')  # 例: '2024-10-27'
            except ValueError:
                # 日付フォーマットが異なる場合のエラーハンドリング
                date_obj = None
        else:
            # 既に datetime オブジェクトの場合
            date_obj = date
        
        if date_obj:
            # 日付のフォーマット
            formatted_date = f"{date_obj.month}月{date_obj.day}日({weekdays[date_obj.weekday()]})"
        else:
            # 変換できない場合は元の文字列を使用
            formatted_date = date
        
        # 時間の処理
        start = entry.start  # startが文字列か time オブジェクトか確認
        end = entry.end      # endが文字列か time オブジェクトか確認
        
        # start_time のフォーマット
        if isinstance(start, str):
            try:
                start_obj = datetime.strptime(start, '%H:%M:%S')
                formatted_start = start_obj.strftime('%H:%M')
            except ValueError:
                formatted_start = start
        else:
            # 既に time オブジェクトの場合
            formatted_start = start.strftime('%H:%M')
        
        # end_time のフォーマット
        if isinstance(end, str):
            try:
                end_obj = datetime.strptime(end, '%H:%M:%S')
                formatted_end = end_obj.strftime('%H:%M')
            except ValueError:
                formatted_end = end

        else:
            # 既に time オブジェクトの場合
            formatted_end = end.strftime('%H:%M')

        
        #total_kinmu=end_obj-start_obj
        total_kinmu = entry.total_kinmu
        time_parts = datetime.strptime(total_kinmu, '%H:%M:%S')
        total_kinmu = timedelta(hours=time_parts.hour, minutes=time_parts.minute, seconds=time_parts.second)


        if total_kinmu.total_seconds() < 0:  
            total_kinmu = timedelta(seconds=abs(total_kinmu.total_seconds()))  # 負の時間を正に変換
  
        # 新しい属性としてformatted_date, formatted_start, formatted_endを追加
        entry.formatted_date = formatted_date
        entry.formatted_start = formatted_start
        entry.formatted_end = formatted_end
        entry.total_kinmu=total_kinmu


        status = entry.status        
        sagyo_entries.append(entry)


    
    context = {
        'total_hours':int(total_hours),
        'total_minutes':int(total_minutes),
        'total_hours_week':int(total_hours_week),
        'total_minutes_week':int(total_minutes_week),
        'total_count':total_count,
        'name':name,
        'sagyo_entries': sagyo_entries,
        'year_month_str': year_month_str,
        'total_count_status_0':total_count_status_0,
    }
    
    return render(request, 'nippo/nhistory.html', context,)


def nipposuccess(request):
    name = request.session.get('name')  # セッションからnameを取得
    trans_option = request.session.get('trans_option')
    data_list = request.session.get('data_list', None)
    if 'data_list' in request.session:
        del request.session['data_list']
    return render(request, 'nippo/nsuccess.html', {'name': name,'data_list':data_list,'trans_option':trans_option})

def nipposuccess_multiple(request):
    name = request.session.get('name')  # セッションからnameを取得
    return render(request, 'nippo/nsuccess_multiple.html', {'name': name})

def nippoinformation(request):
    name = request.session.get('name')  # セッションからnameを取得
    return render(request, 'nippo/ninformation.html', {'name': name})

def nipposettings(request):
    name = request.session.get('name')  # セッションからnameを取得
    return render(request, 'nippo/nsettings.html', {'name': name})

def nippoerror(request):
    name = request.session.get('name')  # セッションからnameを取得
    return render(request, 'nippo/nerror.html', {'name': name})

def nippohelp(request):
    name = request.session.get('name')
    return render(request, 'nippo/nhelp.html', {'name': name})

def nippokoban(request):
    name = request.session.get('name')  # セッションからnameを取得
    koban_numbers = request.session.get('koban_numbers')  # セッションからkoban_numbersを取得  
    return render(request, 'nippo/nkoban.html', {'name': name,'koban_numbers':koban_numbers})


def nippoedit(request,idx):# 編集機能

    if 'action' in request.POST:
            break_time_start=None
            break_time_end=None
    
            name = request.session.get('name')  # セッションからnameを取得
            koban_numbers = request.session.get('koban_numbers')  # セッションからkoban_numbersを取得   
            time_format = "%H:%M"
            date = request.POST.get('content')  # 日付
            start_time = request.POST.get('start_time')  # 開始時間
            end_time = request.POST.get('end_time')  # 終了時間
            start_time = start_time[:5]  # "08:00"
            end_time = end_time[:5]  # "18:00"

            koban0 = request.POST.get('koban0')    # 工番

            attendance = request.POST.getlist('attendance')
        
            koban1 = request.POST.get('koban1')  
            koban_time_start1 = request.POST.get('koban_time_start1') 
            koban_time_end1 = request.POST.get('koban_time_end1') 

            koban2 = request.POST.get('koban2')  
            koban_time_start2 = request.POST.get('break_time_start2') 
            koban_time_end2 = request.POST.get('break_time_end2') 
            lunch_box = request.POST.get('lunch_box')  
            comment = request.POST.get('comment') 

            lunch_time_start = request.POST.get('lunch_time_start')  # 例: "12:00"
            lunch_time_end = request.POST.get('lunch_time_end')      # 例: "13:00"
            lunch_time_start = lunch_time_start[:5]  # "08:00"
            lunch_time_end  = lunch_time_end[:5]  # "18:00"
            #break_time_start = request.POST.get('break_time_start')  # 例: "15:00" or None
            #break_time_end = request.POST.get('break_time_end')      # 例: "15:15" or None

    
    # 文字列を時間形式に変換（Noneの場合はタイムデルタのゼロを使用）
            if lunch_time_start and lunch_time_end:
                lunch_time_start1 = datetime.strptime(lunch_time_start, time_format)
                lunch_time_end1 = datetime.strptime(lunch_time_end, time_format)
                lunch_break_duration = lunch_time_end1 - lunch_time_start1
            else:
                lunch_break_duration = timedelta(0)  # 休憩時間なしとして処理
    
            #if break_time_start and break_time_end:
                #break_time_start = datetime.strptime(break_time_start, time_format)
                #break_time_end = datetime.strptime(break_time_end, time_format)
                #break_duration = break_time_end - break_time_start
            #else:
                #break_duration = timedelta(0)  # 休憩時間なしとして処理
    
    # 合計休憩時間を計算
            total_break_time = lunch_break_duration #+ break_duration
            start_time1 = datetime.strptime(start_time, time_format)
            end_time1 = datetime.strptime(end_time, time_format)
            total_time_kinmu=end_time1-start_time1
            if total_time_kinmu.days < 0:
                total_time_kinmu = timedelta(seconds=total_time_kinmu.seconds) 
            
            total_time =end_time1-start_time1-total_break_time
            if total_time.days < 0:
                total_time = timedelta(seconds=total_time.seconds)  # 負の「日」をリセット
            eight_hours = timedelta(hours=8)
            zangyo=total_time-eight_hours

            start_time = datetime.strptime(start_time,time_format).time()
            end_time = datetime.strptime(end_time, time_format).time()
            
            if lunch_time_start and lunch_time_end:
                break_time_start = datetime.strptime(lunch_time_start, time_format).time()
                break_time_end = datetime.strptime(lunch_time_end, time_format).time()

            trans = request.POST.get('trans') 
            trans_office = request.POST.get('trans_office')    

            # 残業時間がマイナスの場合は0に設定
            if zangyo < timedelta(0):
                zangyo = timedelta(0)
            current_time = (datetime.utcnow() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")

            sagyo = nippo.objects.get(idx=idx)


            sagyo.userid = name
            sagyo.date = date
            sagyo.start = start_time
            sagyo.end = end_time
            sagyo.zangyo = zangyo
            sagyo.total_time = total_time
            sagyo.total_break = total_break_time
            sagyo.koban = koban0
            sagyo.status = 0  # 必要に応じて変更
            sagyo.break_start=break_time_start
            sagyo.break_end=break_time_end
            sagyo.trans = trans
            sagyo.trans_office = trans_office
            sagyo.add_time=current_time
            sagyo.lunch=lunch_box
            sagyo.comment=comment
            sagyo.total_kinmu=total_time_kinmu
            sagyo.save()

            request.session["data_list"] = [
                    {
                    "userid": name,
                    "date": date,
                    "start": start_time.strftime('%H:%M:%S'),
                    "end": end_time.strftime('%H:%M:%S'),
                    "break_start": break_time_start.strftime('%H:%M:%S') if break_time_start else "",
                    "break_end": break_time_end.strftime('%H:%M:%S') if break_time_end else "",
                    "koban": koban0,
                    "trans": trans,
                    "trans_office": trans_office,
                    'lunch' : lunch_box,
                    'comment':comment

                }
            ]  

            return redirect('nsuccess')


    else:
            trans_option = request.session.get('trans_option')
            editentry = get_object_or_404(nippo, idx=str(idx).split('-')[0])
            name = request.session.get('name')  # セッションからnameを取得
            koban_numbers = request.session.get('koban_numbers')  # セッションからkoban_numbersを取得   
            return render(request, 'nippo/nedit.html', {'name': name, 'koban_numbers': koban_numbers,'editentry': editentry,'trans_option':trans_option})

def nippodetail(request,idx):# 履歴から日報詳細情報の閲覧
            editentry = get_object_or_404(nippo, idx=str(idx).split('-')[0])
            trans_option = request.session.get('trans_option')
            name = request.session.get('name')  # セッションからnameを取得
            koban_numbers = request.session.get('koban_numbers')  # セッションからkoban_numbersを取得   
            return render(request, 'nippo/ndetail.html', {'name': name, 'koban_numbers': koban_numbers,'editentry': editentry,'trans_option':trans_option})

def nippodetail_multiple(request,idx):# 履歴から複数入力日報での詳細情報の閲覧

            idx_prefix=idx.split('-')[0]
            request.session['idx_prefix'] = idx_prefix  # nameをセッションに保存  
         

            # idx が "14-1", "14-2", "14-X" のようなものをすべて取得
            editentry = nippo.objects.filter(idx__startswith=f"{idx_prefix}-")  # 部分一致検索
                # 各オブジェクトの属性をリスト化
                # 必要なフィールドをリスト化
            entry_list = [
        {
            'idx': entry.idx,
            'userid': entry.userid,
            'date': entry.date,
            'start': entry.start,
            'end': entry.end,
            'zangyo': entry.zangyo,
            'total_time': entry.total_time,
            'total_break': entry.total_break,
            'koban': entry.koban,
            'add_time': entry.add_time,
            'status': entry.status,
            'break_start': entry.break_start,
            'break_end': entry.break_end,
            'trans': entry.trans,
            'trans_office': entry.trans_office,
            'sequence': entry.sequence,
            'total_kinmu': entry.total_kinmu,
            'lunch':entry.lunch,
            'comment':entry.comment
        }
                for entry in editentry
        ]


            trans_option = request.session.get('trans_option')
            name=request.session.get('name')  
            koban_numbers = request.session.get('koban_numbers')  # セッションからkoban_numbersを取得   
            return render(request, 'nippo/ndetail_multiple.html', {'name': name, 'koban_numbers': koban_numbers,'entry_list': entry_list,'trans_option':trans_option})

def delete_Sagyo(request):
    if request.method == 'POST':
        nippo.objects.all().delete()
    return render(request, 'nippo/calc.html')


def nippoedit_multiple(request,idx):

    if 'action' in request.POST:
            idx_prefix = request.session.get('idx_prefix')
            #print(idx_prefix)
            break_time_start_t=None
            break_time_end_t=None
            if 'idx_prefix' in request.session:
                del request.session['idx_prefix']
            #print(request.POST)  
            total_break_time = timedelta(0)
            break_time_duration_d=timedelta(0)
            break_overlap_flag = request.POST.get('break_overlap_flag', '0')

            name = request.session.get('name')  # セッションからnameを取得
            koban_numbers = request.session.get('koban_numbers')  # セッションからkoban_numbersを取得   
            time_format = "%H:%M"

            date = request.POST.get('content')  # 日付
            trans = request.POST.get('trans') 
            trans_office = request.POST.get('trans_office')

            break_time_start = request.POST.get('break_time_start')  # 例: "12:00"
            break_time_start = f"{break_time_start.split(':')[0]}:{break_time_start.split(':')[1]}" if break_time_start and ':' in break_time_start else None
            break_time_end = request.POST.get('break_time_end')      # 例: "13:00"  
            break_time_end = f"{break_time_end.split(':')[0]}:{break_time_end.split(':')[1]}" if break_time_end and ':' in break_time_end else None

            if break_time_start and break_time_end:
                break_time_start_t=break_time_start+":00"
                break_time_end_t=break_time_end+":00"
            #break_time_start_t= datetime.strptime(break_time_start,time_format).time()
            #break_time_end_t = datetime.strptime(break_time_end, time_format).time()
            lunch_box = request.POST.get('lunch_box')  
            comment = request.POST.get('comment')
            
            if break_time_start and break_time_end:
                break_time_start_d = datetime.strptime(break_time_start, time_format)
                break_time_end_d = datetime.strptime(break_time_end, time_format)
                break_time_duration_d = break_time_end_d - break_time_start_d
            total_break_time = str(break_time_duration_d)
            


 
            total_work_time_d_m_sum = timedelta()


            #start_time = request.POST.get('start_time')  # 開始時間
            #end_time = request.POST.get('end_time')  # 終了時間
            #koban = request.POST.get('koban')    # 工番
            current_time = (datetime.utcnow() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")
            koban_fields = []
            new_prefix = None


            for key in request.POST:
                if key.startswith('sequence'):
                    index = key[8:]  # 'sequence'の後ろの数字部分を取得
                    sequence = request.POST.get(f'sequence{index}')
                    koban = request.POST.get(f'koban{index}')
                    if not koban:
                        continue
                    start_time = request.POST.get(f'start_time{index}')
                    start_time = f"{start_time.split(':')[0]}:{start_time.split(':')[1]}" if start_time and ':' in start_time else None
                    end_time = request.POST.get(f'end_time{index}')
                    end_time = f"{end_time.split(':')[0]}:{end_time.split(':')[1]}" if end_time and ':' in end_time else None
                    start_time_d = datetime.strptime(start_time, time_format)
                    end_time_d = datetime.strptime(end_time, time_format)
                    start_time=start_time+":00"
                    end_time=end_time+":00"
                    #start_time = datetime.strptime(start_time,time_format).time()
                    #end_time = datetime.strptime(end_time, time_format).time()

                    

                    
                    total_work_time_d_m =end_time_d-start_time_d
                    total_work_time_d_m_sum += total_work_time_d_m

                    total_kinmu_time=end_time_d-start_time_d

                    if total_kinmu_time.days < 0:
                        total_kinmu_time = timedelta(seconds=total_kinmu_time.seconds)  # 負の「日」をリセット
                    if total_work_time_d_m.days < 0:
                        total_work_time_d_m = timedelta(seconds=total_work_time_d_m.seconds)  # 負の「日」をリセット
                    


                    new_idx = str(idx_prefix)+"-"+str(sequence)



        # データを収集
                    koban_fields.append({
                        'idx': new_idx,
                        'userid' : name,
                        'sequence': sequence,
                        'date' : date,
                        'koban': koban,
                        'start': start_time,
                        'end': end_time,
                        'trans' : trans,
                        'trans_office' : trans_office,
                        'break_start' : break_time_start_t,
                        'break_end' : break_time_end_t,
                        'total_break':total_break_time,
                        'status' : 0,
                        'add_time' : current_time,
                        'lunch':lunch_box,
                        'comment':comment
                    })
            print(koban_fields)
            try:
    # 全ての sequence を抽出
                
                sequences = sorted(int(field['sequence']) for field in koban_fields)
                print(sequence)

    # 1からスタートし、連続しているかチェック
                expected_sequence = list(range(1, len(sequences) + 1))
                if sequences != expected_sequence:
                    messages.error(request, "中間のチェックボックスを選択することはできません。後ろから順にチェックしてください。")
                    referer = request.META.get('HTTP_REFERER', '/')
                    return redirect(referer)

            except ValueError as e:
    # エラー内容を出力（ログに残す、または例外処理を追加）
                messages.error(request, "中間のチェックボックスを選択することはできません。後ろから順にチェックしてください。")
                referer = request.META.get('HTTP_REFERER', '/')
                return redirect(referer)
            
    # 必要に応じて他のエラー処理（例: リカバリ、ログ出力など）を記述

            #total_work_time_d_m_sum = total_work_time_d_m_sum
            if total_work_time_d_m_sum.days < 0:
               total_work_time_d_m_sum = timedelta(seconds=total_work_time_d_m_sum.seconds) 

            
            if break_overlap_flag=="1":
                total_work_time_d_m_sum = total_work_time_d_m_sum-break_time_duration_d
            else:    
                total_work_time_d_m_sum = total_work_time_d_m_sum
            
            total_work_time = str( total_work_time_d_m_sum)

            eight_hours_d = timedelta(hours=8)

            if break_overlap_flag=="1":
                total_kinmu_time = total_work_time_d_m_sum+break_time_duration_d
            else:    
                total_kinmu_time = total_work_time_d_m_sum+break_time_duration_d  
            
            
            if total_kinmu_time.days < 0:
               total_kinmu_time = timedelta(seconds=total_kinmu_time.seconds)             
            total_kinmu_time = str(total_kinmu_time).zfill(8)


            if break_overlap_flag=="1":
                zangyo = total_work_time_d_m_sum - eight_hours_d
            else:    
                zangyo = total_work_time_d_m_sum - eight_hours_d  


            if zangyo < timedelta(0):
                zangyo = timedelta(0)

            zangyo = str(zangyo)



            for field in koban_fields:
                field['total_time'] = total_work_time
                field['zangyo'] = zangyo
                field['total_kinmu'] = total_kinmu_time
            #print(koban_fields)
            nippo.objects.filter(idx__startswith=f"{idx_prefix}-").delete()
            for field in koban_fields:
                sagyo = nippo(**field)  # 辞書を展開して渡す
                sagyo.save()

            return redirect('nsuccess_multiple')


    else:
            idx_prefix=idx.split('-')[0]
            request.session['idx_prefix'] = idx_prefix  # nameをセッションに保存  
         

            # idx が "14-1", "14-2", "14-X" のようなものをすべて取得
            editentry = nippo.objects.filter(idx__startswith=f"{idx_prefix}-")  # 部分一致検索
                # 各オブジェクトの属性をリスト化
                # 必要なフィールドをリスト化
            entry_list = [
        {
            'idx': entry.idx,
            'userid': entry.userid,
            'date': entry.date,
            'start': entry.start,
            'end': entry.end,
            'zangyo': entry.zangyo,
            'total_time': entry.total_time,
            'total_break': entry.total_break,
            'koban': entry.koban,
            'add_time': entry.add_time,
            'status': entry.status,
            'break_start': entry.break_start,
            'break_end': entry.break_end,
            'trans': entry.trans,
            'trans_office': entry.trans_office,
            'sequence': entry.sequence,
            'total_kinmu': entry.total_kinmu,
            'lunch':entry.lunch,
            'comment':entry.comment
        }
                for entry in editentry
        ]
            #print(entry_list)
            length = len(entry_list)
            length = length+2 # HTML側へ合わせる



            trans_option = request.session.get('trans_option')
            name=request.session.get('name')  
            koban_numbers = request.session.get('koban_numbers')  # セッションからkoban_numbersを取得   
            return render(request, 'nippo/nedit_multiple.html', {'name': name, 'koban_numbers': koban_numbers,'entry_list': entry_list,'trans_option':trans_option,'length':length})
    

