import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

df1 = pd.read_csv("average_monthly_nominal_wage_2000_2016.csv", encoding='cp1251', sep=';')
df2 = pd.read_csv("average_monthly_nominal_wage_2017_2023.csv", encoding='cp1251', sep=';')

st.title('Проанализируем динамику уровня средних зарплат в разрезе по видам экономической деятельности за последние 30 лет в России.')

st.markdown('Сначала посмотрим во сколько раз увеличилась средняя зарплата во всех экономических сферах.')


def plt_salary_growth(df, years):
    ratio = [df.iloc[i, -1] / df.iloc[i, 1] for i in range(df.shape[0])]
    fig = plt.figure(figsize = (10, 5))
    plt.bar(df.index, ratio, color='c')
    plt.ylabel(f'Во сколько раз увеличилась зарплата за {years}')
    plt.xlabel('Экономические деятельности')
    st.pyplot(fig)


plt_salary_growth(df1, '2000-2016')
plt_salary_growth(df2,  '2017-2023')

df = df1.merge(df2, how='inner', on='Деятельность')
economic_sectors = st.sidebar.multiselect('Выберете экономические деятельности', df['Деятельность'], default='Всего по экономике')
df.set_index('Деятельность', inplace=True)
years = list(map(int, df.columns))

st.markdown('Построим графики изменения зарплаты по годам для выбранных видов экономической деятельности.')


def plot_sector_part(df, sector, years):
    col = (np.random.random(), np.random.random(), np.random.random())
    nominal_salary = df[df.index == sector].values[0]
    plt.plot(years, nominal_salary, color=col)


fig = plt.figure(figsize=(10, 5))
for sector in economic_sectors:
    plot_sector_part(df, sector, years)
plt.title('Изменение средней зарплаты без учета инфляции')
plt.legend(economic_sectors)
plt.grid(True)
st.pyplot(fig)

st.markdown("""Можно отметить, что несмотря на общий тренд роста, зарплаты в сфере рыболовства сильно растут после 2014 года.
 Также можно выделить резкий скачок вниз зарплат в сфере производства нефтепродуктов в 2018 году.""")

st.warning(' Надо учесть инфляцию для подсчета реальной динамики зарплат.')

inflation = pd.read_csv("Inflation_rate.csv")
inflation.set_index('Год', inplace=True)
inflation = inflation.iloc[24::-1]
inflation_temps = inflation['Всего'].values

show_real_salary = st.sidebar.checkbox('Показать реальную динамику зарплат с учетом инфляции')

if show_real_salary:

    st.markdown('Пересчитаем средние зарплаты с учетом уровня инфляции в выбранных сферах экономической деятельности.')

    def plot_sector_salary(df, sector, inflation_temps, years):
        nominal_salary = df[df.index == sector].values[0]
        n = len(nominal_salary)

        inflation_salary = [nominal_salary[0]] * n
        for i in range(1, n):
            inflation_salary[i] = inflation_salary[i - 1] * (1 + inflation_temps[i] / 100)

        real_salary = [nominal_salary[i] - (inflation_salary[i] - nominal_salary[0]) for i in range(n)]

        fig = plt.figure(figsize=(10, 5))
        plt.plot(years, nominal_salary, color='blue')
        plt.plot(years, real_salary, color='red')
        plt.title(sector)
        plt.legend(['Номинальная зарплата', 'Реальная зарплата с учетом инфляции'])
        plt.grid(True)
        st.pyplot(fig)


    for sector in economic_sectors:
        plot_sector_salary(df, sector, inflation_temps, years)

show_comparison = st.sidebar.checkbox('Показать влияние инфляции на изменение зарплаты по сравнению с предыдущим годом')

if show_comparison:

    st.markdown("""Проанализируем влияние инфляции на изменение зарплаты по сравнению с предыдущим годом.
     Для этого можно поделить зарплату на коэффициент инфляции и выяснить реальную зарплату без
    учёта обесценивания денег, и сравнить эту реальную зарплату с прошлогодней.""")


    def plot_real_salary_change(df, sector, inflation_temps, years):
        nominal_salary = df[df.index == sector].values[0]
        n = len(nominal_salary)
        comparison = [nominal_salary[i] - nominal_salary[i - 1] * (1 + inflation_temps[i - 1] / 100) for i in range(1, n)]

        fig = plt.figure(figsize= (15, 5))
        sns.barplot(x=years[1:], y=comparison, hue=comparison, palette='hls')
        plt.title(sector)
        st.pyplot(fig)


    for sector in economic_sectors:
        plot_real_salary_change(df, sector, inflation_temps, years)

    st.markdown("""Для всех видов экономической деятельности заметно падение зарплат после кризисных годов (2008 и 2014).
    Также здесь более ярко выражено падение средней зарплаты в сфере производства нефтепродуктов,
     и заметно, что зарплаты рыбаков растут быстрее, чем средняя зарплата по России, несмотря на кризисы.""")