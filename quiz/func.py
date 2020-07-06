from .models import Answer

def get_quiz_dict(quiz_list):
    """
    仮引数:
        quiz_list ([list型]): [各要素がquizインスタンスであるリストを受け取り]

    戻り値:
        quiz_dict ([dict型]): [keyがquizインスタンス, valueにPV数・正答率を持つ辞書を返却]
    """
    quiz_dict = {}
    for quiz in quiz_list:
        quiz_id = quiz.id
        answer = Answer.objects.filter(quiz=quiz_id) # 問題IDでフィルターした回答履歴
        total_count = answer.count() # 総回答数
        correct_count = answer.filter(is_correct=True).count() # 正解の回答数
        try:
            correct_rate = f'{correct_count / total_count * 100:03.0f}%'
        except ZeroDivisionError:
            correct_rate = "まだ回答がありません"
        quiz_dict[quiz] = {
            'total_count': total_count,
            'correct_rate': correct_rate,
        }
        print(quiz_dict)
    return quiz_dict

