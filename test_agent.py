#!/usr/bin/env python3
"""
🎯 SAILIGHT TEST-AGENT
======================
Automatisierter Test-Agent, der Docker-Container baut, startet und testet.
Führe aus: python test_agent.py
"""

import subprocess
import sys
import time
import json
import requests
from pathlib import Path
from typing import Optional, Dict, List
import platform


class TestAgent:
    """Automatisierter Test-Agent für Sailight"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.is_windows = platform.system() == "Windows"
        self.results = {
            "success": False,
            "steps": [],
            "errors": [],
            "warnings": [],
            "start_time": time.time(),
            "end_time": None
        }
        
    def print_header(self, text: str):
        """Druckt eine Überschrift"""
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}\n")
    
    def print_step(self, step: str):
        """Druckt einen Schritt"""
        print(f"  [TEST] {step}...")
    
    def print_success(self, message: str):
        """Druckt eine Erfolgsmeldung"""
        print(f"  [OK] {message}")
        self.results["steps"].append({"status": "success", "message": message})
    
    def print_error(self, message: str):
        """Druckt eine Fehlermeldung"""
        print(f"  [ERROR] {message}")
        self.results["errors"].append(message)
        self.results["steps"].append({"status": "error", "message": message})
    
    def print_warning(self, message: str):
        """Druckt eine Warnung"""
        print(f"  [WARN] {message}")
        self.results["warnings"].append(message)
    
    def run_command(self, command: str, cwd: Optional[str] = None, 
                   check: bool = False, capture: bool = False, timeout: int = 300) -> subprocess.CompletedProcess:
        """Führt einen Befehl aus"""
        print(f"  [RUN] Führe aus: {command}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or str(self.base_dir),
                check=check,
                capture_output=capture,
                text=True,
                timeout=timeout
            )
            if capture and result.stdout:
                print(f"  [OUTPUT] {result.stdout}")
            return result
        except subprocess.TimeoutExpired:
            self.print_error(f"Timeout nach {timeout} Sekunden: {command}")
            return subprocess.CompletedProcess(command, 1, "", "Timeout")
        except Exception as e:
            self.print_error(f"Fehler bei '{command}': {e}")
            return subprocess.CompletedProcess(command, 1, "", str(e))
    
    def check_docker(self):
        """Prüft, ob Docker verfügbar ist"""
        self.print_step("Docker-Verfügbarkeit prüfen")
        result = self.run_command("docker --version", capture=True)
        if result.returncode == 0:
            self.print_success(f"Docker ist verfügbar: {result.stdout.strip()}")
            return True
        else:
            self.print_error("Docker ist nicht installiert oder nicht verfügbar")
            return False
    
    def check_docker_compose(self):
        """Prüft, ob Docker Compose verfügbar ist"""
        self.print_step("Docker Compose-Verfügbarkeit prüfen")
        
        # Versuche docker-compose
        result = self.run_command("docker-compose --version", capture=True)
        if result.returncode == 0:
            self.print_success(f"docker-compose ist verfügbar: {result.stdout.strip()}")
            return "docker-compose"
        
        # Versuche docker compose (Plugin)
        result = self.run_command("docker compose version", capture=True)
        if result.returncode == 0:
            self.print_success(f"docker compose (Plugin) ist verfügbar: {result.stdout.strip()}")
            return "docker compose"
        
        self.print_error("Docker Compose ist nicht installiert")
        return None
    
    def build_containers(self, compose_cmd: str):
        """Baut die Docker-Container"""
        self.print_step("Docker-Container bauen")
        
        # Erst Cache bereinigen
        self.run_command(f"{compose_cmd} down -v --rmi all", capture=True)
        
        # Container bauen
        result = self.run_command(
            f"{compose_cmd} build --no-cache",
            capture=True,
            timeout=1800  # 30 Minuten Timeout
        )
        
        if result.returncode == 0:
            self.print_success("Container erfolgreich gebaut")
            return True
        else:
            self.print_error(f"Build fehlgeschlagen: {result.stderr}")
            return False
    
    def start_containers(self, compose_cmd: str):
        """Startet die Docker-Container"""
        self.print_step("Docker-Container starten")
        
        result = self.run_command(
            f"{compose_cmd} up -d",
            capture=True,
            timeout=300
        )
        
        if result.returncode == 0:
            self.print_success("Container erfolgreich gestartet")
            return True
        else:
            self.print_error(f"Start fehlgeschlagen: {result.stderr}")
            return False
    
    def check_container_status(self, compose_cmd: str):
        """Prüft den Status der Container"""
        self.print_step("Container-Status prüfen")
        
        result = self.run_command(f"{compose_cmd} ps", capture=True)
        if result.returncode == 0:
            print(f"\n{result.stdout}")
            
            # Prüfe, ob backend läuft
            if "sailight_backend" in result.stdout and "Up" in result.stdout:
                self.print_success("Backend-Container läuft")
                return True
            else:
                self.print_error("Backend-Container läuft nicht")
                return False
        else:
            self.print_error(f"Status-Abfrage fehlgeschlagen: {result.stderr}")
            return False
    
    def wait_for_backend(self, max_attempts: int = 30, delay: int = 5):
        """Wartet, bis Backend bereit ist"""
        self.print_step(f"Warte auf Backend (max {max_attempts * delay}s)...")
        
        for attempt in range(max_attempts):
            try:
                response = requests.get("http://localhost:8000/api/health", timeout=5)
                if response.status_code == 200:
                    self.print_success(f"Backend ist bereit! (Versuch {attempt + 1})")
                    return True
            except Exception:
                if attempt < max_attempts - 1:
                    time.sleep(delay)
                    print(f"  [WAIT] Versuch {attempt + 1}/{max_attempts}...")
                else:
                    self.print_error("Backend hat nicht innerhalb der Wartezeit reagiert")
                    return False
        
        return False
    
    def test_api_endpoints(self):
        """Testet wichtige API-Endpunkte"""
        self.print_step("API-Endpunkte testen")
        
        endpoints = [
            ("Health Check", "http://localhost:8000/api/health"),
            ("Root", "http://localhost:8000/"),
            ("API Docs", "http://localhost:8000/api/docs"),
        ]
        
        success_count = 0
        for name, url in endpoints:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    self.print_success(f"{name} ({url}) → OK (Status: {response.status_code})")
                    success_count += 1
                else:
                    self.print_warning(f"{name} ({url}) → Status: {response.status_code}")
            except Exception as e:
                self.print_error(f"{name} ({url}) → Fehler: {e}")
        
        if success_count == len(endpoints):
            self.print_success(f"Alle {len(endpoints)} API-Endpunkte funktionieren!")
            return True
        else:
            self.print_warning(f"Nur {success_count}/{len(endpoints)} Endpunkte funktionieren")
            return False
    
    def test_database(self, compose_cmd: str):
        """Testet die Datenbank-Verbindung"""
        self.print_step("Datenbank-Verbindung testen")
        
        result = self.run_command(
            f"{compose_cmd} exec postgres psql -U sailight_user -d sailight -c 'SELECT COUNT(*) FROM cabinet;'",
            capture=True
        )
        
        if result.returncode == 0:
            count = result.stdout.strip()
            self.print_success(f"Datenbank-Verbindung OK (Schaltschränke: {count})")
            return True
        else:
            self.print_error(f"Datenbank-Verbindung fehlgeschlagen: {result.stderr}")
            return False
    
    def show_logs(self, compose_cmd: str, service: str = "backend"):
        """Zeigt die Logs eines Services"""
        self.print_step(f"Logs von {service} anzeigen")
        result = self.run_command(f"{compose_cmd} logs --tail=20 {service}", capture=True)
        if result.returncode == 0:
            print(f"\n{result.stdout}")
    
    def generate_report(self):
        """Generiert einen Test-Report"""
        self.results["end_time"] = time.time()
        duration = self.results["end_time"] - self.results["start_time"]
        
        self.print_header("TEST-REPORT")
        
        print(f"\n[TIME]")
        print(f"  Start: {time.ctime(self.results['start_time'])}")
        print(f"  Ende:  {time.ctime(self.results['end_time'])}")
        print(f"  Dauer: {duration:.2f} Sekunden ({duration/60:.2f} Minuten)")
        
        print(f"\n[SUMMARY]")
        print(f"  Erfolge: {len([s for s in self.results['steps'] if s['status'] == 'success'])}")
        print(f"  Fehler:   {len(self.results['errors'])}")
        print(f"  Warnungen: {len(self.results['warnings'])}")
        
        if self.results["errors"]:
            print(f"\n[ERRORS]")
            for error in self.results["errors"]:
                print(f"  - {error}")
        
        if self.results["warnings"]:
            print(f"\n[WARNINGS]")
            for warning in self.results["warnings"]:
                print(f"  - {warning}")
        
        self.results["success"] = len(self.results["errors"]) == 0
        
        if self.results["success"]:
            print(f"\n[STATUS] SUCCESS")
        else:
            print(f"\n[STATUS] FAILED")
        
        return self.results
    
    def run_full_test(self):
        """Führt den kompletten Test durch"""
        self.print_header("SAILIGHT TEST-AGENT GESTARTET")
        
        # 1. Docker prüfen
        if not self.check_docker():
            self.generate_report()
            return False
        
        # 2. Docker Compose prüfen
        compose_cmd = self.check_docker_compose()
        if not compose_cmd:
            self.generate_report()
            return False
        
        # 3. Container bauen
        if not self.build_containers(compose_cmd):
            self.show_logs(compose_cmd, "backend")
            self.generate_report()
            return False
        
        # 4. Container starten
        if not self.start_containers(compose_cmd):
            self.show_logs(compose_cmd, "backend")
            self.generate_report()
            return False
        
        # 5. Container-Status prüfen
        if not self.check_container_status(compose_cmd):
            self.show_logs(compose_cmd, "backend")
            self.generate_report()
            return False
        
        # 6. Auf Backend warten
        if not self.wait_for_backend():
            self.show_logs(compose_cmd, "backend")
            self.generate_report()
            return False
        
        # 7. API testen
        self.test_api_endpoints()
        
        # 8. Datenbank testen
        self.test_database(compose_cmd)
        
        # 9. Report generieren
        results = self.generate_report()
        
        return results["success"]


if __name__ == "__main__":
    print("""
    ============================================================
    SAILIGHT TEST-AGENT v1.0
    ============================================================
    Automatisierter Test für Docker-Setup und API
    ============================================================
    """)
    
    agent = TestAgent()
    success = agent.run_full_test()
    
    sys.exit(0 if success else 1)
