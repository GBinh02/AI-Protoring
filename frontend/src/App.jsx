import { lazy, Suspense, useState } from "react";
import {
  Shield,
  GraduationCap,
  UserCog,
  ArrowRight,
  CheckCircle2,
  LockKeyhole,
  AlertCircle,
} from "lucide-react";
const StudentExam = lazy(() => import("./components/StudentExam"));
const ProctorDashboard = lazy(() => import("./components/ProctorDashboard"));

export default function App() {
  const [role, setRole] = useState("student");
  const [code, setCode] = useState("");
  const [fullName, setFullName] = useState("");
  const [proctorToken, setProctorToken] = useState("");
  const [activeRole, setActiveRole] = useState(null);
  const [error, setError] = useState("");
  const normalizedCode = code.trim().toUpperCase();
  const handleLogout = () => {
    setActiveRole(null);
    setCode("");
    setFullName("");
    setProctorToken("");
    setError("");
  };
  function handleLogin(event) {
    event.preventDefault();
    if (!normalizedCode.startsWith(role === "student" ? "SV" : "GV")) {
      setError(
        `Mã ${role === "student" ? "sinh viên phải bắt đầu bằng SV" : "giảng viên phải bắt đầu bằng GV"}.`,
      );
      return;
    }
    if (role === "student" && !fullName.trim()) {
      setError("Vui lòng nhập họ và tên.");
      return;
    }
    if (role === "proctor" && !proctorToken.trim()) {
      setError("Vui lòng nhập mã xác thực giảng viên.");
      return;
    }
    setError("");
    setActiveRole(role);
  }
  if (activeRole === "student")
    return (
      <Suspense fallback={<LoadingScreen />}>
        <StudentExam
          studentId={normalizedCode}
          studentName={fullName.trim()}
          onLogout={handleLogout}
        />
      </Suspense>
    );
  if (activeRole === "proctor")
    return (
      <Suspense fallback={<LoadingScreen />}>
        <ProctorDashboard
          teacherId={normalizedCode}
          authToken={proctorToken.trim()}
          onLogout={handleLogout}
        />
      </Suspense>
    );
  return (
    <main className="login-page">
      <section className="login-story">
        <a href="#" className="brand">
          <span className="brand-mark">
            <Shield size={25} />
          </span>
          EduShield<span className="brand-ai">AI</span>
        </a>
        <div className="story-content">
          <span className="eyebrow">KHÔNG GIAN THI TRỰC TUYẾN</span>
          <h1>
            Tập trung làm bài
            <br />
            <em>An tâm mỗi kỳ thi</em>
          </h1>
          <p>
            Một không gian kết nối sinh viên và giảng viên, từ chuẩn bị đề thi
            đến giám sát và đánh giá kết quả.
          </p>
          <div className="story-illustration" aria-hidden="true">
            <div className="illustration-top">
              <span className="illustration-dot" />
              <span>Không gian học thuật</span>
              <Shield size={18} />
            </div>
            <div className="illustration-body">
              <div className="illustration-icon">
                <GraduationCap size={38} />
              </div>
              <div>
                <strong>Sẵn sàng cho điều tiếp theo</strong>
                <span>Chuẩn bị · Làm bài · Hoàn thành</span>
              </div>
            </div>
            <div className="illustration-track">
              <i />
              <i />
              <i />
            </div>
            <div className="illustration-bottom">
              <CheckCircle2 size={16} /> Rõ ràng trong từng bước
            </div>
          </div>
          <div className="story-features">
            <span>
              <CheckCircle2 size={17} /> Giám sát bằng AI
            </span>
            <span>
              <CheckCircle2 size={17} /> Quản lý kỳ thi tập trung
            </span>
          </div>
        </div>
        <footer>
          EDUSHIELD AI <span>Học tập chủ động - Đánh giá minh bạch.</span>
        </footer>
      </section>
      <section className="login-form-area">
        <div className="login-form-wrap">
          <span className="eyebrow">CHÀO MỪNG BẠN TRỞ LẠI</span>
          <h2>Bắt đầu phiên làm việc</h2>
          <p className="login-subtitle">
            Chọn vai trò và nhập thông tin để tiếp tục.
          </p>
          <div className="role-picker" aria-label="Vai trò đăng nhập">
            {[
              ["student", "Sinh viên", GraduationCap],
              ["proctor", "Giảng viên", UserCog],
            ].map(([key, label, Icon]) => (
              <button
                key={key}
                type="button"
                aria-pressed={role === key}
                className={role === key ? "selected" : ""}
                onClick={() => {
                  setRole(key);
                  setCode("");
                  setError("");
                }}
              >
                <Icon size={19} />
                {label}
              </button>
            ))}
          </div>
          <form onSubmit={handleLogin} className="login-form">
            <label htmlFor="identity">
              Mã {role === "student" ? "sinh viên" : "giảng viên"}
            </label>
            <input
              id="identity"
              autoComplete="username"
              required
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder={role === "student" ? "VD: SV-2151220053" : "VD: GV-2026"}
              aria-invalid={!!error}
              aria-describedby={error ? "login-error" : undefined}
            />
            {role === "student" ? (
              <>
                <label htmlFor="full-name">Họ và tên</label>
                <input
                  id="full-name"
                  autoComplete="name"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Nhập đầy đủ họ và tên"
                />
              </>
            ) : (
              <>
                <label htmlFor="proctor-token">Mã xác thực</label>
                <input
                  id="proctor-token"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={proctorToken}
                  onChange={(e) => setProctorToken(e.target.value)}
                  placeholder="Mã xác thực do quản trị viên cung cấp"
                />
              </>
            )}
            {error && (
              <p className="form-error" id="login-error" role="alert">
                <AlertCircle size={17} />
                {error}
              </p>
            )}
            <button className="primary-button login-submit" type="submit">
              {role === "student" ? "Vào không gian thi" : "Vào trang quản lý"}
              <ArrowRight size={18} />
            </button>
          </form>
          <p className="login-note">
            <LockKeyhole size={16} />
            {role === "student"
              ? "Bạn sẽ nhập mã đề thi ở bước tiếp theo."
              : "Mã xác thực được kiểm tra khi tải dữ liệu quản lý."}
          </p>
        </div>
        <p className="login-help">
          EduShield AI · Hệ thống giám sát thi trực tuyến
        </p>
      </section>
    </main>
  );
}

function LoadingScreen() {
  return (
    <div className="route-loading" role="status">
      <Shield size={32} />
      <p>Đang mở không gian làm việc…</p>
    </div>
  );
}
