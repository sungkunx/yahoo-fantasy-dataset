#!/usr/bin/env python3
# run_schedule.py - 스케줄링된 데이터 수집 실행

import os
import sys
import subprocess
from datetime import datetime, timedelta
import pytz

def log_message(message):
    """로그 메시지 출력"""
    kst = pytz.timezone('Asia/Seoul')
    timestamp = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S KST")
    print(f"[{timestamp}] {message}")

def should_run_snapshot():
    """현재 시각이 스냅샷을 실행해야 할 시간인지 확인"""
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)

    # 한국 시간 기준 오후 6시 이후에만 실행 (NBA 경기 종료 후)
    if now.hour < 18:
        log_message(f"아직 경기 시간입니다. 현재: {now.hour}시, 18시 이후 실행됩니다.")
        return False

    # 주말은 제외 (월-금요일만)
    if now.weekday() >= 5:  # 5=토요일, 6=일요일
        log_message("주말에는 데이터 수집을 하지 않습니다.")
        return False

    return True

def run_data_collection():
    """데이터 수집 스크립트들을 순차적으로 실행"""
    scripts = [
        ("get_week_dates.py", "주차 정보 업데이트"),
        ("snapshot.py", "스냅샷 데이터 수집"),
        ("transactions.py", "거래 정보 수집")
    ]

    success_count = 0

    for script, description in scripts:
        log_message(f"{description} 시작: {script}")
        try:
            result = subprocess.run([sys.executable, script],
                                  capture_output=True, text=True, timeout=1800)  # 30분 타임아웃

            if result.returncode == 0:
                log_message(f"{description} 완료: {script}")
                success_count += 1
            else:
                log_message(f"{description} 실패: {script}")
                log_message(f"오류: {result.stderr}")

        except subprocess.TimeoutExpired:
            log_message(f"{description} 타임아웃: {script}")
        except Exception as e:
            log_message(f"{description} 예외 발생: {script} - {e}")

    log_message(f"데이터 수집 완료: {success_count}/{len(scripts)} 성공")
    return success_count == len(scripts)

def main():
    """메인 실행 함수"""
    log_message("스케줄된 데이터 수집 시작")

    # 현재 디렉토리 확인
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    log_message(f"작업 디렉토리: {script_dir}")

    # 실행 조건 확인
    if not should_run_snapshot():
        log_message("실행 조건이 맞지 않아 종료합니다.")
        return

    # 데이터 수집 실행
    success = run_data_collection()

    if success:
        log_message("모든 데이터 수집이 성공적으로 완료되었습니다.")
    else:
        log_message("일부 데이터 수집에서 오류가 발생했습니다.")

if __name__ == "__main__":
    main()