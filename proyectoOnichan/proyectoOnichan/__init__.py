try:
	import pymysql
	pymysql.install_as_MySQLdb()
except Exception:
	# If PyMySQL isn't available, Django will error when connecting to MySQL.
	pass

