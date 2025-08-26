# 📘 Middleware 개발 문서

## 🔧 개발 환경
- **언어**: Python
- **목적**: 두 개의 DB 시스템을 연결하여 이벤트 처리용 미들웨어 개발

---

## 🗄️ 데이터베이스 구조

### 1. Database A (MSSQL)
- **DBMS**: Microsoft SQL Server  
- **호스트**: `kdnavien.iptime.org:1533`  
- **DB 이름**: `KDNAVIEN`  
- **접속 정보**:  
  - Username: `navien`  
  - Password: `tlaqlwm2174`  

---

### 2. Database B (MariaDB)
- **DBMS**: MariaDB  
- **호스트**: `kdnavien.iptime.org:3336`  
- **DB 이름**: `simbizlocal`  
- **접속 정보**:  
  - Username: `root`  
  - Password: `tlaqlwm2174`  

---

## 📋 주요 기능
1. **Scheduler 기반 조회**  
   - B 데이터베이스(`simbizlocal`)의 `alram_event` 테이블을 주기적으로 조회  

2. **조건 필터링**  
   - `push_yn` 컬럼 값이 `'N'`인 레코드만 검색  

3. **결과 처리**  
   - `push_yn = 'N'`인 이벤트 건수를 집계 및 반환  

---
