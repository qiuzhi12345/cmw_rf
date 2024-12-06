# -- coding: utf-8 --
import os
import time
from collections import OrderedDict
from baselib.loglib.log_lib import *

class csvreport(object):
    """


    用于生成 CSV 格式 的 表格

    例如：

    ======== ======== ========
    value0    value1   value2
    -------- -------- --------
    XXX1        1         2
    XXX2        2         3
    ======== ======== ========

    写入一行的条件：

    - 当写入的 所有的列都被写入数据之后（会形成一行数据）。
    - 再写入一个新的数据，该行会被写入文件。

    :logname:
          输出log的名字，支持带文件夹。

          比如，当 logname = ”atest/a“，会在log文件下自动生成
          atest 文件夹，并且生成 a.csv 文件

    :mode:
        当行所有列没有被写完的时候，如果再写一个已经写过的列数据：

        - 0: 新的数据会替换掉老的数据。
        - 1: 现有行会被写入文件，现有行中没有填写的数据默认使用上一次的。写入数据会形成新的一行。

    """
    def __init__(self, logname, mode = 0):
        self.__logname = logname
        self.__check_logname()
        logtime= time.strftime('_%Y_%m_%d_%H_%M_%S',time.localtime());
        self.filename='./log/'+logname+logtime+'.csv';
        self._fid = open(self.filename, 'w')
        self.__rdict = OrderedDict()
        self.__line = 0
        self.mode = mode

    def __check_logname(self):
        logname_s = self.__logname.split("/")
        if len(logname_s) > 1:
            full_path = "./log/"
            for path in logname_s[:-1]:
                full_path = full_path + path.strip() + "/"
                if not os.path.exists(full_path):
                    logwarn("mkdir %s"%(full_path))
                    os.mkdir(full_path)

    def add_col(self, col_name):
      """
      增加列标题：

      :col_name:
          列标题名字

      例如::

        add_col("a")
        add_col(["a", "b"])

      """
      if type(col_name) == list:
          name_list = col_name
      else:
          name_list = [col_name]

      if self.__line == 0:
          for name in name_list:
              if  not self.__rdict.has_key(name):
                  self.__rdict[name] = [None, False]
              else:
                  logwarn("col %s is exsit already"%name)
      else:
          logerror("can't add col any more")


    def write_value(self, column, value):
      """
      写列的值。

      当列的标题不存在时，会自动添加列标题：

      :column:
          列名字
      :value:
          写入值

      例如::

          write_value("a", 1)
          write_value(["a", 'b'], [1, 2])
      """
      c_list = type(column) == list
      v_list = type(value) == list
      if c_list != v_list:
          logerror("the type of colume and value must the same type(list)")
      if c_list:
          if len(column) != len(value):
              logerror("len error, column=%d value=%d"%(len(column), len(value)))
              return
          column_list = column
          value_list = value
      else:
          column_list = [column]
          value_list = [value]

      for index, col in enumerate(column_list):
          value = value_list[index]
          if type(value) == list or type(value) == tuple :
              value=str(value).replace(',','-')
              value=str(value).replace(" ","")

          if not self.__rdict.has_key(col):
              logwarn("not found the column %s"%(col))
              logwarn("auto add column \" %s \""%col)
              if self.__line == 0:
                  self.__rdict[col] = [value, True]
              else:
                  logerror("can't add col any more")
                  return

          else:
              for k,v in self.__rdict.items():
                  if v[1] == False:
                    break;
              else:
                  self.__write_out()

              if self.__rdict[col][1] != False:
                  if self.mode == 0:
                      logwarn("\" %s \" already has value \" %s \", will be replaced to \" %s \""%(col, self.__rdict[col], value))
                  else:
                      self.__write_out()
                      logwarn("some cols is using old value!!")
              self.__rdict[col] = [value, True]



    def __write_out(self):
        if len(self.__rdict.keys()) != 0:
            if self.__line == 0:
                logdebug("column %s"%(self.__rdict.keys()))
                self._fid.write(self.__list2str(self.__rdict.keys(), 0)+"\n")

            logdebug("%s: %s"%(self.__line, self.__rdict.values()))
            self._fid.write(self.__list2str(self.__rdict.values(), 1)+"\n")
            self.__line = self.__line + 1
            for k,v in self.__rdict.items():
                self.__rdict[k][1] = False


    def __list2str(self,lst, type = 0):
        stri = ""
        for i in lst:
            if type == 0:
                stri = stri + str(i) + ','
            else:
                stri = stri + str(i[0]) + ','
        stri = stri[:-1]
        return stri

    def flush_line(self):
        '''
        不管当前行是否满足写入条件，将现有数据强行写入一行。
        '''
        self.__write_out()
        self._fid.flush()

    def deinit(self):
        '''
        释放log文件
        '''
        self.flush_line()
        self._fid.close()


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.deinit()