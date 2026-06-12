import sys

from job_posting.crew import JobPostingCrew


def run():
    # Replace with your inputs, it will automatically interpolate any tasks and agents information
    inputs = {
        'company_domain':'https://www.zhipoai.cn/',
        'company_description': "智学优课主要的技术研究和人才培养的方向为：大模型、AIGC、网絡安全、人工智能、Java编程、Python编程、安卓APP开发、前端开发等。开课以来课程辐射200余万，累计培养20万余I人才，与国内1000余家IT相关企业建立了人才合作关系。",
        'hiring_needs': '大模型应用开发工程师：计算机、人工智能相关专业，本科学历及以上，熟练掌握prompt、RAG、微调等技术，有大型语言模型的开发、部署经验者优先。',
        'specific_benefits':'周末双休、五险一金、节日福利、带薪年假、团建聚餐',
    }
    JobPostingCrew().crew().kickoff(inputs=inputs)



def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'company_domain':'https://www.zhipoai.cn/',
        'company_description': "智学优课主要的技术研究和人才培养的方向为：大模型、AIGC、网絡安全、人工智能、Java编程、Python编程、安卓APP开发、前端开发等。开课以来课程辐射200余万，累计培养20万余I人才，与国内1000余家IT相关企业建立了人才合作关系。",
        'hiring_needs': '大模型应用开发工程师：计算机、人工智能相关专业，本科学历及以上，熟练掌握prompt、RAG、微调等技术，有大型语言模型的开发、部署经验者优先。',
        'specific_benefits':'周末双休、五险一金、节日福利、带薪年假、团建聚餐',
    }
    try:
        JobPostingCrew().crew().train(n_iterations=int(sys.argv[1]), inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")
