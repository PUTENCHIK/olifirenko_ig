# !pip install wordcloud
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS


df = pd.read_csv('output_processed.csv')
df.info()

wordcloud = WordCloud(background_color='black',
                      colormap = 'spring',
                      width = 800,
                      height = 600,
                      collocations = False,
                      stopwords = STOPWORDS).generate(' '.join(df['event'].str.lower()))

plt.figure(figsize=(20,10))
plt.title("Облако слов событий")
plt.imshow(wordcloud)
plt.axis("off")
plt.show()

#@title Круговая диаграмма характеристики с выбором сложности { run: "auto", vertical-output: true }
#@markdown ###Сложность
"""
@markdown |#|Сложность|
@markdown |---|:----|
@markdown |1|Обычный
@markdown |2|Эксперт
@markdown |3|Мастер
"""

difficulty = "Мастер" #@param ["Обычный", "Эксперт", "Мастер"]
#@markdown ###Характеристика
"""
@markdown |#|Характеристика|
@markdown |---|:----|
@markdown |1|Урон
@markdown |2|Здоровье
@markdown |3|Защита
@markdown |4|Поглощение отбрасывания
@markdown |5|Награда
"""

attribute = "Здоровье" #@param ["Урон", "Здоровье", "Защита", "Поглощение отбрасывания", "Награда"]
field = f"{difficulty.lower()}_{attribute.lower()}"
df_not_na = df[df[field].notna()]
df_sorted = df_not_na.sort_values(by=field,
                                  ascending=False)

name_list = df_sorted['name'].tolist()

min_amount = 3
max_amount = 10
amount = min_amount
total = df_sorted[field].sum()
cumulative_percentage = 0
for i in range(max_amount):
    if i > max_amount:
        break
    percentage = df_sorted[field].iloc[i] / total * 100
    cumulative_percentage += percentage
    amount = i + 1
    if cumulative_percentage > 85:
        break

data = df_sorted[field].tolist()[:amount]
labels = name_list[:amount]
if cumulative_percentage > 85:
    data += [(100-cumulative_percentage)*total]
    labels += ["Остальные"]

plt.pie(data,
        labels=labels,
        radius = 1,
        autopct='%1.1f%%',
        startangle=90,)

plt.title(f'{attribute} для сложности {difficulty}')
plt.show()

#@title Сравнение двух мобов { run: "auto", vertical-output: true }
import ipywidgets as widgets
from math import pi
from IPython.display import display, clear_output


def mobe_1_change(value):
    global mobe_1
    mobe_1 = value['new']
    update()

def mobe_2_change(value):
    global mobe_2
    mobe_2 = value['new']
    update()

def difficulty_change(value):
    global difficulty
    difficulty = value['new']
    update()

def update():
    clear_output(wait=True)
    dpl()
    if mobe_1 == mobe_2:
        print("Выберите разных мобов")
        return
    draw_visualization()

def normalize_column(column):
    min_val = 0
    max_val = column.max()
    return 5 * (column - min_val) / (max_val - min_val)

def draw_visualization():
    titles = ["Урон", "Здоровье", "Защита", "Поглощение отбрасывания", "Награда"]
    cols = [f"{difficulty.lower()}_{title.lower()}" for title in titles]
    data = df[df['name'].isin([mobe_1, mobe_2])].set_index('name')[cols][:2]

    data.fillna(0, inplace=True)
    print(mobe_1, mobe_2)

    data = data.apply(normalize_column)
    data = data.transpose()

    N = len(cols)

    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    ax = plt.subplot(111, polar=True)

    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)

    plt.xticks(angles[:-1], titles)

    ax.set_rlabel_position(0)
    plt.yticks([i for i in range(1, 6)], color="grey", size=7)
    plt.ylim(0,6)

    values=data[data.columns[0]].values.flatten().tolist()
    values += values[:1]
    ax.plot(angles, values, linewidth=1, linestyle='solid', label=data.columns[0])
    ax.fill(angles, values, 'b', alpha=0.1)

    values=data[data.columns[1]].values.flatten().tolist()
    values += values[:1]
    ax.plot(angles, values, linewidth=1, linestyle='solid', label=data.columns[1])
    ax.fill(angles, values, 'r', alpha=0.1)

    plt.legend(bbox_to_anchor=(0.1, 0.1))
    plt.title((f"Сравнение характеристик {mobe_1} и {mobe_2}\n"
               f"на сложности {difficulty}"),
              y=1.1)
    plt.show()


df = df[df[field].notna()]
names = df['name'].tolist()
difficulties = ['Обычный', 'Эксперт', 'Мастер']

mobe_1, mobe_2, difficulty = names[0], names[0], difficulties[0]

mobe_1_select = widgets.Dropdown(
    options=names,
    description='Первый моб:',
    disabled=False,
)
mobe_2_select = widgets.Dropdown(
    options=names,
    description='Второй моб:',
    disabled=False,
)
difficulty_select = widgets.Dropdown(
    options=difficulties,
    description='Сложность:',
    disabled=False,
)

def dpl():
    display(mobe_1_select,
            mobe_2_select,
            difficulty_select)

mobe_1_select.observe(mobe_1_change, names='value')
mobe_2_select.observe(mobe_2_change, names='value')
difficulty_select.observe(difficulty_change, names='value')

update()
