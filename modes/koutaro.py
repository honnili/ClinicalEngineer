def render_koutaro():
    st.subheader("光太郎モード（連続演習）")

    num_questions = st.slider("出題数を選んでください", 1, 5, 3, key="koutaro_num")
    big_field = st.selectbox("大分類を選んでください", list(field_dict.keys()), key="koutaro_big")
    sub_field = st.selectbox("中分類を選んでください", field_dict[big_field], key="koutaro_sub")
    answer_mode = st.radio("解答形式を選んでください", ["選択式", "記述式"], horizontal=True, key="koutaro_mode")

    # 問題生成ボタン
    if st.button("問題を生成する", key="koutaro_generate"):
        st.session_state["koutaro_questions"] = []
        for i in range(num_questions):
            qdata = generate_question(big_field, sub_field)
            if qdata:
                st.session_state["koutaro_questions"].append(qdata)
        # 回答状態をリセット
        st.session_state["koutaro_answers"] = {}

    # --- 問題表示 ---
    questions = st.session_state.get("koutaro_questions", [])
    for i, qdata in enumerate(questions):
        st.markdown(f"### 第{i+1}問")
        st.write(f"**Q: {qdata['question']}**")

        if answer_mode == "選択式":
            with st.form(f"choice_form_{i}"):
                choice = st.radio("選択肢", qdata["options"], key=f"choice_{i}")
                submitted = st.form_submit_button("解答する")
                if submitted:
                    st.session_state["koutaro_answers"][i] = {"mode": "choice", "value": choice}

            # 解答済みなら結果表示
            ans = st.session_state.get("koutaro_answers", {}).get(i)
            if ans and ans["mode"] == "choice":
                correct = (ans["value"] == qdata["answer"])
                if correct:
                    st.success("正解！ 🎉")
                else:
                    st.error(f"不正解… 正解は {qdata['answer']} です")
                st.info(qdata.get("improvement", "ここを復習しましょう"))

        else:  # 記述式
            with st.form(f"text_form_{i}"):
                text = st.text_area("解答を入力してください", key=f"text_{i}")
                submitted = st.form_submit_button("採点する")
                if submitted:
                    st.session_state["koutaro_answers"][i] = {"mode": "text", "value": text}

            ans = st.session_state.get("koutaro_answers", {}).get(i)
            if ans and ans["mode"] == "text":
                score, feedback = grade_free_answer(ans["value"], qdata["answer"])
                st.write(f"採点結果: {score}%")
                st.info(feedback)

        # 質問・メモ欄
        st.text_area("質問・メモ", key=f"memo_{i}")