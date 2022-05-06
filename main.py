import streamlit as st
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import seaborn as sns
import emoji
from collections import Counter
from urlextract import URLExtract
extractor = URLExtract()



def preprocess(data):
    split = '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s\-\s'
    messages = re.split(split, data)[1:]
    dates = re.findall(split, data)
    df = pd.DataFrame({'Messages':messages, 'Date':dates})
    df['Date'] = pd.to_datetime(df['Date'], format = '%m/%d/%y, %H:%M - ')
    user_name = []
    messages = []
    split2 = '([\w\W]+?):\s'
    for i in df['Messages']:
        x = re.split(split2, i)
        if x[1:]:
            user_name.append(x[1])
            messages.append(x[2])
        else:
            user_name.append('Group Update')
            messages.append(x[0])
    df['User'] = user_name
    df['Message'] = messages
    df.drop('Messages', axis = 1, inplace = True)
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month_name()
    df['Day'] = df['Date'].dt.day
    df['Day_name'] = df['Date'].dt.day_name()
    df['Hour'] = df['Date'].dt.hour
    df['Minute'] = df['Date'].dt.minute
    df['Month_num'] = df['Date'].dt.month

    return df

st.sidebar.title('WhatsApp Chat Analysis')

f = st.sidebar.file_uploader('Choose a file')

if f is not None:
    bytes_data = f.getvalue()
    data = bytes_data.decode('utf-8')

    df = preprocess(data)

    # st.header("Your Data:")
    

    user_list = df['User'].unique().tolist()
    user_list.sort()
    try:
        user_list.remove('Group Update')
    except:
        pass
    user_list.insert(0,"Everyone")


    if st.sidebar.checkbox("Show entered data"):
        st.title("Your Data")
        st.dataframe(df)
    st.sidebar.markdown("***")


    username = st.sidebar.selectbox("Show Analysis for which User:", user_list)
    
    

    if st.sidebar.button("Analyze"):
        # st.markdown("""---""")
        st.title("Showing results for {}:".format(username))

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("#### Total Messages")
            if username == 'Everyone':
                st.title(df.shape[0])
            else:
                st.title(df[df['User'] == username].shape[0])

        with col2:
            st.markdown("#### Total Words")
            if username == 'Everyone':
                words = []
                for i in df['Message']:
                    words.extend(i.split())
                st.title(len(words))
            else:
                words = []
                for i in df[df['User'] == username]['Message']:
                    words.extend(i.split())
                st.title(len(words))

        with col3:
            st.markdown("#### Total Media")
            if username == 'Everyone':
                media = df[df['Message'] == '<Media omitted>\n'].shape[0]
                st.title(media)
            else:
                new_df = df[df['User'] == username]
                media = new_df[df['Message'] == '<Media omitted>\n'].shape[0]
                st.title(media)

        with col4:
            st.markdown("#### Total Links")
            if username == 'Everyone':
                y = []
                for i in df['Message']:
                    y.extend(extractor.find_urls(i))
                st.title(len(y))
            else:
                new_df = df[df['User'] == username]
                y = []
                for i in new_df['Message']:
                    y.extend(extractor.find_urls(i))
                st.title(len(y))

        st.markdown("***")
        col5, col6 = st.columns(2)

        with col5:
            if username == "Everyone":
                st.header("Most Active Users")
                z = df['User'].value_counts().head()
                fig, ax = plt.subplots()
                ax.bar(z.index, z.values)
                plt.xticks(rotation="vertical")
                st.pyplot(fig)

        with col6:
            if username == "Everyone":
                st.header("Percentage of messages per user")
                st.dataframe(((df['User'].value_counts()/df.shape[0])*100).reset_index().rename(columns={"index" : 'Name of User', 'user' : 'Percentage of messages'}))

        col7, col8 = st.columns(2)
        
        with col7:
            if username == "Everyone":
                emojis = []
                st.title("Most used Emojis")
                for i in df['Message']:
                    emojis.extend([x for x in i if x in emoji.UNICODE_EMOJI['en']])
                emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
                st.dataframe(emoji_df.head())
            else:
                new_df = df[df['User'] == username]
                emojis = []
                st.title("Most used Emojis")
                for i in new_df['Message']:
                    emojis.extend([x for x in i if x in emoji.UNICODE_EMOJI['en']])
                emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
                st.dataframe(emoji_df)
        
        with col8:
            st.title("Monthly Timeline")
            if username == 'Everyone':
                
                timeline = df.groupby(['Year', 'Month_num', 'Month']).count()['Message'].reset_index()
                time = []
                for i in range(timeline.shape[0]):
                    time.append(str(timeline['Month'][i])+" - "+str(timeline['Year'][i]))
                timeline['Time'] = time
                
                fig, ax = plt.subplots()
                ax.plot(timeline['Time'], timeline['Message'], color = "green")
                plt.xticks(rotation="vertical")
                st.pyplot(fig)
            else:
                
                new_df = df[df['User'] == username]
                timeline = new_df.groupby(['Year', 'Month_num', 'Month']).count()['Message'].reset_index()
                time = []
                for i in range(timeline.shape[0]):
                    time.append(str(timeline['Month'][i])+" - "+str(timeline['Year'][i]))
                timeline['Time'] = time
                
                fig, ax = plt.subplots()
                ax.plot(timeline['Time'], timeline['Message'], color = "green")
                plt.xticks(rotation="vertical")
                st.pyplot(fig)

        col9, col10 = st.columns(2)
        
        with col9:
            st.title("Most Busy Days")
            if username == 'Everyone':
                fig, ax = plt.subplots()
                temp = df['Day_name'].value_counts()
                ax.bar(temp.index, temp.values, color = 'red')
                plt.xticks(rotation="vertical")
                st.pyplot(fig)
            else:
                new_df = df[df['User'] == username]
                fig, ax = plt.subplots()
                temp = new_df['Day_name'].value_counts()
                ax.bar(temp.index, temp.values, color = 'red')
                plt.xticks(rotation="vertical")
                st.pyplot(fig)
                
        with col10:
            st.title("Message percentage of days")
            if username == 'Everyone':
                day_df = pd.DataFrame(((df['Day_name'].value_counts()/df.shape[0])*100).reset_index().rename(columns={"index" : 'Day', 'Day_name' : 'Percentage of messages'}))
                st.dataframe(day_df)
            else:
                new_df = df[df['User'] == username]
                day_df = pd.DataFrame(((new_df['Day_name'].value_counts()/new_df.shape[0])*100).reset_index().rename(columns={"index" : 'Day', 'Day_name' : 'Percentage of messages'}))
                st.dataframe(day_df)

        col11, col12 = st.columns(2)

        with col11:
            st.title("Message percentage of months")
            if username == 'Everyone':
                month_df = pd.DataFrame(((df['Month'].value_counts()/df.shape[0])*100).reset_index().rename(columns={"index" : 'Month', 'Month' : 'Percentage of messages'}))
                st.dataframe(month_df)
            else:
                new_df = df[df['User'] == username]
                month_df = pd.DataFrame(((new_df['Month'].value_counts()/new_df.shape[0])*100).reset_index().rename(columns={"index" : 'Month', 'Month' : 'Percentage of messages'}))
                st.dataframe(month_df)

        with col12:
            st.title("Most Busy Months")
            if username == 'Everyone':
                fig, ax = plt.subplots()
                temp = df['Month'].value_counts()
                ax.bar(temp.index, temp.values, color = 'gold')
                plt.xticks(rotation="vertical")
                st.pyplot(fig)
            else:
                new_df = df[df['User'] == username]
                fig, ax = plt.subplots()
                temp = new_df['Month'].value_counts()
                ax.bar(temp.index, temp.values, color = 'gold')
                plt.xticks(rotation="vertical")
                st.pyplot(fig)

        st.markdown("<h1 style='text-align:center'>Time range of activity - Heat Map</h1>", unsafe_allow_html=True)
        
        if username == "Everyone":
            new_df = df
        else:
            new_df = df[df['User'] == username]
        
        period = []
        for i in new_df[['Day_name', 'Hour']]['Hour']:
            if i == 23:
                period.append(str(i)+"-00")
            elif i == 0:
                period.append('00-'+str(i+1))
            else:
                period.append(str(i)+"-"+str(i+1))
        new_df['Period'] = period
        heatmap_df = (new_df.pivot_table(index='Day_name', columns='Period', values='Message', aggfunc='count').fillna(0))
        fig, ax = plt.subplots()
        ax = sns.heatmap(heatmap_df)
        st.pyplot(fig)



