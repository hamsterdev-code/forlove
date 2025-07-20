from sqlalchemy import create_engine



engine = create_engine(
    "mysql+pymysql://gen_user:hamsterdev1@89.169.45.136:3306/default_db", #   sqlite:///server.db
    connect_args={"ssl": {"required": True}}  # или {"ssl": True}
)