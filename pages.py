import streamlit as st

def render_home():
    st.markdown(
        '<div style="background: linear-gradient(135deg, #0284C7 0%, #082F49 100%); '
        'padding: 40px; border-radius: 16px; color: white; text-align: center; '
        'margin-bottom: 30px; box-shadow: 0 8px 32px rgba(2, 132, 199, 0.3);">'
        '<h2 style="margin: 0; font-size: 36px; font-weight: 900;">71wm AI Weather Model</h2>'
        '<p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;">Real-time Weather Intelligence for UAE</p>'
        '</div>',
        unsafe_allow_html=True
    )
    
    st.markdown("<h3 style='color: #082F49; margin-top: 30px;'>System Status</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            '<div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); '
            'padding: 20px; border-radius: 12px; color: white; text-align: center; '
            'box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);">'
            '<div style="font-size: 28px; font-weight: 900;">OK</div>'
            '<div style="font-size: 24px; font-weight: 900; margin: 10px 0;">Active</div>'
            '<div style="font-size: 14px; opacity: 0.9;">System Status</div>'
            '</div>',
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            '<div style="background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); '
            'padding: 20px; border-radius: 12px; color: white; text-align: center; '
            'box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);">'
            '<div style="font-size: 28px; font-weight: 900;">36</div>'
            '<div style="font-size: 24px; font-weight: 900; margin: 10px 0;">Stations</div>'
            '<div style="font-size: 14px; opacity: 0.9;">Monitoring</div>'
            '</div>',
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            '<div style="background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); '
            'padding: 20px; border-radius: 12px; color: white; text-align: center; '
            'box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);">'
            '<div style="font-size: 28px; font-weight: 900;">5</div>'
            '<div style="font-size: 24px; font-weight: 900; margin: 10px 0;">Days</div>'
            '<div style="font-size: 14px; opacity: 
