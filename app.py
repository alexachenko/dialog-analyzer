import streamlit as st
import pandas as pd
import io
from database import DialogDatabase
from analyzer import DialogAnalyzer

st.set_page_config(page_title="Анализ диалогов", layout="wide")

st.markdown("""
<style>
    .main-title { font-size: 2rem; text-align: center; margin-bottom: 1.5rem; }
    .problem-card { background: #ffebee; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; }
    .similar-card { background: #f5f5f5; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; }
    div[data-testid="stMetricValue"] { color: #000000 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Анализ диалогов</div>', unsafe_allow_html=True)

@st.cache_resource
def init():
    return DialogDatabase(), DialogAnalyzer()

db, analyzer = init()

with st.sidebar:
    st.header("Загрузка")
    uploaded = st.file_uploader("CSV с колонкой 'dialog'", type=['csv'])
    
    if uploaded:
        content = uploaded.getvalue().decode('utf-8')
        df_preview = pd.read_csv(io.StringIO(content))
        st.success(f"{len(df_preview)} диалогов")
        st.dataframe(df_preview, use_container_width=True, height=250)
        
        if st.button("Анализировать", type="primary", use_container_width=True):
            with st.spinner("Анализ..."):
                db.load_dialogs(io.StringIO(content))
                results = [analyzer.analyze_dialog(d) for d in df_preview['dialog']]
                df_preview['тема'] = [r['topic'] for r in results]
                df_preview['эмоция'] = [r['emotion'] for r in results]
                df_preview['проблемный'] = [r['is_problem'] for r in results]
                st.session_state.df = df_preview
                st.success("Готово!")
                st.rerun()

if 'df' in st.session_state:
    df = st.session_state.df
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Всего", len(df))
    with c2: st.metric("Проблемных", df['проблемный'].sum())
    with c3: st.metric("Негативных", (df['эмоция'] == 'негативный').sum())
    with c4: st.metric("Позитивных", (df['эмоция'] == 'позитивный').sum())
    
    st.divider()
    
    tab1, tab2, tab3, tab4 = st.tabs(["Диалоги", "Проблемные", "Статистика", "Поиск"])
    
    with tab1:
        display = df[['dialog', 'тема', 'эмоция']].copy()
        display.index = range(1, len(display) + 1)
        st.dataframe(display, use_container_width=True, height=500)
    
    with tab2:
        problems = df[df['проблемный'] == True]
        if len(problems) > 0:
            for _, row in problems.iterrows():
                st.markdown(f"""
                <div class="problem-card">
                    <strong>{row['тема']}</strong> | {row['эмоция']}<br>
                    {row['dialog'][:200]}...
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Нет проблемных")
    
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Темы")
            for topic, count in df['тема'].value_counts().items():
                st.write(f"{topic}: {count}")
        with col2:
            st.subheader("Эмоции")
            for emo, count in df['эмоция'].value_counts().items():
                st.write(f"{emo}: {count}")
    
    with tab4:
        st.subheader("Поиск")
        query = st.text_input("Введите текст", placeholder="брак, доставка, возврат...")
        if query:
            with st.spinner("Поиск..."):
                similar = db.find_similar(query, top_k=5)
                if similar:
                    for i, (text, score) in enumerate(similar, 1):
                        st.markdown(f"""
                        <div class="similar-card">
                            <strong>#{i} - {score}%</strong><br>
                            {text[:300]}...
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Ничего не найдено")

else:
    st.info("Загрузите CSV файл")