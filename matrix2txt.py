# -*- coding: cp1251 -*-
# Copyrigth Yuri Ryazantsev

# class Matrix begin ------------------------------------------------------------------------------
class Matrix():
    def _read_razdel(self, razdel):
        '''чтение раздела из матрицы'''
        # формирование заголовка поиска (описание раздела)
        zag = '! 0000 ' + self.js["OTCHET"] + ' ' + razdel + ' ' + self.js["YEAR"][2:4] + ' ' +\
              self.js["MONTH"] + ' ' + self.js["REGION"] + ';'

        t_matrix = {}
        # поиск раздела
        start_str = False
        m_array = []
        for i in range(0, len(self.tm)):
            #print('i=', i)
            if start_str:
                if '! 000' in self.tm[i]:
                    break
                else:
                    tmp_str = self.tm[i].replace(';','')
                    t_array = tmp_str.rsplit()
                    m_array.append(t_array)
            else:
                #print(self.tm[i], len(self.tm) - 2)
                if zag in self.tm[i] and i < len(self.tm) - 2:
                    start_str = True
        if m_array:
            t_matrix[razdel] = m_array
            #print(t_matrix)
            #print(m_array)
        else:
            t_matrix[razdel] = []
        return t_matrix[razdel]

    def _check_razdel(self, matrix, rzd_key):
        ''' Проверка разедла - соответсвие количества строк и граф файлу описания''' 
        cnt_grf = int(self.js[rzd_key]["CNT_GRF"])
        cnt_str = int(self.js[rzd_key]["CNT_STR"])
        #print("RAZDEL:", rzd_key, "  GRAF:",cnt_grf, "    STROK:",cnt_str)
        # Проверяем количество граф и непривышение номера строки
        error_flag = False
        for i in matrix:
            # нумерация строк
            if int(i[0]) > cnt_str:
                print('Ошибка проверки матрицы. Превышение количества строк. Задано:', cnt_str, ' Имеется:', i[0])
                print('   Раздел:', rzd_key, '   Строка:', i)
                error_flag = True
            # количество граф
            if (len(i) - 1) != cnt_grf:
                print('Ошибка проверки матрицы. Неверное количество граф. Задано:', cnt_grf, ' Имеется:', (len(i) - 1))
                print('   Раздел:', rzd_key, '   Строка:', i)
                error_flag = True
        # зануляем матрицу в случае ошибки
        if error_flag:
            matrix = []
        return matrix

    def _fill_razdel(self, matrix, rzd_key):
        ''' Заполнение пропущенных строк нулями''' 
        cnt_grf = int(self.js[rzd_key]["CNT_GRF"])
        cnt_str = int(self.js[rzd_key]["CNT_STR"])
        zero_str = list('0' * cnt_grf)
        tmp_matrix = []
        pred_str = 0
        for i in matrix:
            cur_str = int(i[0])
            propusk = cur_str - pred_str
            if propusk < 1:
                print('Ошибка в разделе', rzd_key, 'Номер текущей строки:', cur_str, ' не больше предыдущей строки:', pred_str)
                return []
            if propusk > 1:
                for j in range(pred_str + 1, cur_str):
                    m_str = [str(j)] + zero_str
                    tmp_matrix.append(m_str)
            pred_str = cur_str
            tmp_matrix.append(i)
        ''' в итоге имеем массив, соотвестующий файлу описания'''
        return tmp_matrix           
    
    def get_cell(self, razdel, stroka, grafa):
        ''' считываем ячейку из матрицы, раздел, стока и графа могут быть как числовые так и строковые'''
        try:
            if type(razdel) is int:
                razdel = str(razdel)
            if type(grafa) is str:
                grafa = int(grafa)
            if type(stroka) is str:
                stroka = int(stroka)
            razdel = razdel.rjust(2, '0')
            # уменьшаем строку на 1 (т.к. элементы массива начинаются с нуля)
            stroka -= 1
        except:
            print('Ошибка приведения типов при считывании ячейки. Раздел:', razdel, '  Cтрока:', stroka, '  Графа:', grafa)
            #raise
            return None
        cell = None
        try:
            cell = self.matrix[razdel][stroka][grafa]
        except:
            print('Ошибка при считывании ячейки. Раздел:', razdel, '  Cтрока:', stroka, '  Графа:', grafa)
            raise
        finally:
            return cell
                        


    def __init__(self, jsonf):
        ''' инициализация матрицы, на вход передается описание отчета'''
        self.js = jsonf       
        m_filename = self.js["MATRIX"].replace("%MATRIX_PATH%",self.js["MATRIX_PATH"])
        # m_filename = m_filename.replace('/','\\')
        try:
           mf = open(m_filename, 'r', encoding='cp1251')
        except:
           print('Ошибка открытия файла матрицы:', m_filename)
           raise
           sys.exit()
        self.tm = mf.readlines()
        for i in self.tm:
           i.replace('\n','')
        self.matrix = {}
        # 
        for i in self.js['RAZDELS']:
            self.matrix[i] = self._read_razdel(i)
            self.matrix[i] = self._check_razdel(self.matrix[i], i)
            self.matrix[i] = self._fill_razdel(self.matrix[i], i)
            #print(matrix[i])
            #for j in self.matrix[i]:
            #    print(j)

           
# class Matrix end --------------------------------------------------------------------------------



def check_global_dir():
    if  not os.path.isdir("META"):
        print("Ошибка выполнения! Отсутствует каталог описания отчетов: META")
        return False
    '''if  not os.path.isdir("LOG"):
        os.mkdir("LOG")
        print("Создан каталог: LOG")
    if  not os.path.isdir("TXT"):
        os.mkdir("TXT")
        print("Создан каталог: TXT")'''
    return True

def check_argv(argv):
    # проверка переданных параметров
    if len(argv) != 4:
        print('\nВ программу должно быть передано три аргумента - код отчета, год, месяц')
        print('Пример: matrix2txt.py 495 2015 06')
        print('-------------------------------------------------------------------------------------------------')
        print('Код отчета, год, месяц используются для формирования имени файла описания запроса в каталоге META')
        print('../META/495/495_2015_06.json')
        return False
    return True

def read_meta(argv):
    f_name = argv[1] + '_' + argv[2] + '_' + argv[3] + '.json'
    f_path = 'META/' + argv[1] + '/' + f_name
    try:
        f = open(f_path, 'r', encoding = 'cp1251')
    except:
        print('Ошибка отрытия файла описния отчета:', f_path)
        raise
        return False
    try:
        js = json.load(f)
        return js
    except:
        print("Ошибка разбора файла описания отчета.")
        print("смотри структуру файла json\n")
        raise
        return False

def get_datetime():
    ''' Получаем текущее дату-время в формате  YYYYY-MM-DD hh:mm.cc'''
    import time
    #c_dtime = time.localtime()[:6]
    #c_dtime = str(c_dtime).replace(',','').replace(' ','').replace('(','').replace(')','')
    tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec = time.localtime()[:6]
    c_dtime = str(tm_year) +'-' + str(tm_mon).rjust(2,'0') + '-' +str(tm_mday).rjust(2,'0') + ' ' +str(tm_hour).rjust(2,'0') + ':'
    c_dtime = c_dtime + str(tm_min).rjust(2,'0') + '.' + str(tm_sec).rjust(2,'0')
    return c_dtime


class Log_to_file(object):
    # обертка вокруг стандартного вывода
    # text -> stdout   преобразуется в  text -> file,stdout
    def __init__(self,log_file):
        self._file = log_file
    def write(self, line):
        self._file.write(line)
        sys.__stdout__.write(line)
    def flush(self):
        self._file.flush()
        sys.__stdout__.flush()

def PrintException():
    # Печатает последнее исключение в файл
    import linecache
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('    EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj),file=log_file)


if __name__ == '__main__':
    # открываем Лог-файл в текущей директории для отображения ошибки передачи параметров в программу
    import sys
    import time
    import os
    import json

    # проверка наличия глобальных директорий
    if not check_global_dir():
        sys.exit()

    # проверка аргументов
    if not check_argv(sys.argv):
        sys.exit()

    # читаем файл параметров в переменную
    meta = read_meta(sys.argv)
    if not meta:
        sys.exit()
      
    m_matrix = Matrix(meta)  
    m_cell = m_matrix.get_cell(1, 1, 221)
    print(m_cell)
    m_cell = m_matrix.get_cell(1, 1, 221)
    print(m_cell)
    m_cell = m_matrix.get_cell(1, 1, 221)
    print(m_cell)
