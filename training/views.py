import time
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Avg, Max
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from core.models import Course, Site
from .models import Participant, Enrollment, Question, Option, Assessment, Answer, AssistanceEvent, AuditLog
from .serializers import LoginSerializer, RegisterSerializer, IdentifySerializer, SubmitSerializer
from .qr import verify_token, sign_token

def _norm_curp(curp: str) -> str:
    return (curp or "").strip().upper().replace(" ", "")

def _curp_format_ok(curp: str) -> bool:
    import re
    return bool(re.match(r'^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$', curp or ""))

def _resolve_qr(token: str):
    payload = verify_token(token)
    qr_type = payload.get("qr_type")
    course_id = payload.get("course_id")
    site_id = payload.get("site_id")
    if qr_type not in ("PRE","POST"):
        raise ValueError("QR inválido")
    course = get_object_or_404(Course, id=course_id)
    if not course.is_active:
        raise ValueError("Curso inactivo")
    site_fixed = None
    sites = None
    if site_id:
        site_fixed = get_object_or_404(Site, id=site_id)
    else:
        sites = list(Site.objects.all().values("id","name"))
    return qr_type, course, sites, site_fixed

@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    ser = LoginSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    user = authenticate(request, email=ser.validated_data["email"], password=ser.validated_data["password"])
    if not user:
        return Response({"detail":"Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)
    refresh = RefreshToken.for_user(user)
    return Response({"token": str(refresh.access_token), "refresh": str(refresh)})

@api_view(["GET"])
@permission_classes([AllowAny])
def public_qr_resolve(request):
    token = request.query_params.get("token","")
    try:
        qr_type, course, sites, site_fixed = _resolve_qr(token)
        return Response({
            "qr_type": qr_type,
            "course": {"id": course.id, "name": course.name},
            "sites": sites,
            "site_fixed": {"id": site_fixed.id, "name": site_fixed.name} if site_fixed else None,
            "active": True,
        })
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([AllowAny])
def public_register(request):
    ser = RegisterSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    token = ser.validated_data["token"]
    name = ser.validated_data["name"].strip()
    role = ser.validated_data["role"].strip()
    curp = _norm_curp(ser.validated_data["curp"])
    site_id = ser.validated_data["site_id"]

    if not _curp_format_ok(curp):
        return Response({"detail":"CURP inválida"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        qr_type, course, sites, site_fixed = _resolve_qr(token)
        if qr_type != "PRE":
            return Response({"detail":"Este QR no es para registro"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    if site_fixed and int(site_id) != site_fixed.id:
        return Response({"detail":"Sede no coincide con el QR"}, status=status.HTTP_400_BAD_REQUEST)

    site = get_object_or_404(Site, id=site_id)
    participant, _ = Participant.objects.get_or_create(curp=curp, defaults={"name": name, "role": role})
    # update name/role if changed (optional)
    participant.name = name
    participant.role = role
    participant.save()

    try:
        Enrollment.objects.create(participant=participant, course=course, site=site)
    except Exception:
        # already enrolled
        pass

    return Response({"ok": True})

@api_view(["GET"])
@permission_classes([AllowAny])
def public_test(request, qtype):
    token = request.query_params.get("token","")
    try:
        qr_type, course, sites, site_fixed = _resolve_qr(token)
        if qtype != qr_type:
            return Response({"detail":"QR no corresponde a este test"}, status=status.HTTP_400_BAD_REQUEST)
        qs = Question.objects.filter(course=course, qtype=qtype).order_by("id")
        questions = []
        for q in qs:
            questions.append({
                "id": q.id,
                "text": q.text,
                "options": [{"id": o.id, "text": o.text} for o in q.options.all().order_by("id")]
            })
        return Response({"questions": questions})
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([AllowAny])
def public_identify(request):
    ser = IdentifySerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    token = ser.validated_data["token"]
    curp = _norm_curp(ser.validated_data["curp"])
    if not _curp_format_ok(curp):
        return Response({"detail":"CURP inválida"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        qr_type, course, sites, site_fixed = _resolve_qr(token)
        if qr_type != "POST":
            return Response({"detail":"Este QR no es para evaluación final"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    participant = Participant.objects.filter(curp=curp).first()
    if not participant:
        return Response({"detail":"No hay registro previo con ese CURP"}, status=status.HTTP_404_NOT_FOUND)

    enrollment = Enrollment.objects.filter(participant=participant, course=course).first()
    if not enrollment:
        return Response({"detail":"No hay registro previo para este curso"}, status=status.HTTP_404_NOT_FOUND)

    # mark assistance once
    AssistanceEvent.objects.get_or_create(enrollment=enrollment)
    return Response({"ok": True})

@api_view(["POST"])
@permission_classes([AllowAny])
def public_submit(request, qtype):
    ser = SubmitSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    token = ser.validated_data["token"]
    curp = _norm_curp(ser.validated_data["curp"])
    answers_in = ser.validated_data["answers"]

    if not _curp_format_ok(curp):
        return Response({"detail":"CURP inválida"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        qr_type, course, sites, site_fixed = _resolve_qr(token)
        if qtype != qr_type:
            return Response({"detail":"QR no corresponde a este test"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    participant = Participant.objects.filter(curp=curp).first()
    if not participant:
        return Response({"detail":"No hay registro previo"}, status=status.HTTP_404_NOT_FOUND)

    enrollment = Enrollment.objects.filter(participant=participant, course=course).first()
    if not enrollment:
        return Response({"detail":"No hay inscripción previa para este curso"}, status=status.HTTP_404_NOT_FOUND)

    # Load questions map
    qset = {q.id: q for q in Question.objects.filter(course=course, qtype=qtype).prefetch_related("options")}
    if not qset:
        return Response({"detail":"No hay preguntas cargadas"}, status=status.HTTP_400_BAD_REQUEST)

    total = len(qset)
    correct = 0

    # Validate and score
    chosen = {}
    for item in answers_in:
        qid = int(item.get("question_id"))
        oid = int(item.get("option_id"))
        if qid not in qset:
            continue
        # ensure option belongs
        opt = Option.objects.filter(id=oid, question_id=qid).first()
        if not opt:
            continue
        chosen[qid] = opt

    if len(chosen) != total:
        return Response({"detail":"Responde todas las preguntas"}, status=status.HTTP_400_BAD_REQUEST)

    for qid, opt in chosen.items():
        if opt.is_correct:
            correct += 1

    score = int(round((correct / total) * 100))
    assessment = Assessment.objects.create(
        enrollment=enrollment, qtype=qtype, score=score, correct_count=correct, total=total
    )
    for qid, opt in chosen.items():
        Answer.objects.create(
            assessment=assessment, question_id=qid, option=opt, is_correct=opt.is_correct
        )

    return Response({"score": score, "correct_count": correct, "total": total})

# ---------------- Admin endpoints ----------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_catalog_courses(request):
    return Response({"courses": list(Course.objects.all().values("id","name"))})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_catalog_sites(request):
    return Response({"sites": list(Site.objects.all().values("id","name"))})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def admin_generate_qr(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)
    qr_type = request.data.get("qr_type")
    site_id = request.data.get("site_id")
    expires_in_days = int(request.data.get("expires_in_days", settings.QR_DEFAULT_EXP_DAYS))
    if qr_type not in ("PRE","POST"):
        return Response({"detail":"qr_type debe ser PRE o POST"}, status=400)

    exp = int(time.time() + expires_in_days * 86400)
    payload = {"qr_type": qr_type, "course_id": course.id, "exp": exp, "iat": int(time.time())}
    if site_id:
        payload["site_id"] = int(site_id)

    token = sign_token(payload)
    # Public page lives at /p?token=...
    base_url = request.build_absolute_uri("/").rstrip("/")
    qr_url = f"{base_url}/p?token={token}"
    AuditLog.objects.create(action="GENERATE_QR", meta={"course_id": course.id, "qr_type": qr_type, "site_id": site_id, "exp": exp})
    return Response({"token": token, "qr_url": qr_url})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_report_results(request):
    # filters
    course_id = request.query_params.get("course_id")
    site_id = request.query_params.get("site_id")
    date_from = request.query_params.get("from")
    date_to = request.query_params.get("to")

    enroll_qs = Enrollment.objects.select_related("participant","course","site").all()
    if course_id:
        enroll_qs = enroll_qs.filter(course_id=int(course_id))
    if site_id:
        enroll_qs = enroll_qs.filter(site_id=int(site_id))
    if date_from:
        enroll_qs = enroll_qs.filter(registered_at__date__gte=date_from)
    if date_to:
        enroll_qs = enroll_qs.filter(registered_at__date__lte=date_to)

    rows = []
    for e in enroll_qs.order_by("-registered_at")[:5000]:
        pre = Assessment.objects.filter(enrollment=e, qtype="PRE").order_by("-submitted_at").first()
        post = Assessment.objects.filter(enrollment=e, qtype="POST").order_by("-submitted_at").first()
        assist = AssistanceEvent.objects.filter(enrollment=e).exists()
        pre_score = pre.score if pre else None
        post_score = post.score if post else None
        delta = (post_score - pre_score) if (post_score is not None and pre_score is not None) else None

        rows.append({
            "curp": e.participant.curp,
            "name": e.participant.name,
            "role": e.participant.role,
            "site": e.site.name,
            "pre_score": pre_score,
            "post_score": post_score,
            "delta": delta,
            "assistance": assist,
            "pre_at": pre.submitted_at.isoformat() if pre else None,
            "post_at": post.submitted_at.isoformat() if post else None,
        })

    return Response({"rows": rows})
