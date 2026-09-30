"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { RegionMensaje } from "@/src/components/auth/RegionMensaje";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { Select } from "@/src/components/ui/Select";
import { ApiRequestError } from "@/src/lib/http";
import { crearFichaPersonal, crearUsuarioIdentidad, listarCargos, listarUnidades } from "@/src/lib/administracion-api";
import type { Cargo, Unidad } from "@/src/lib/administracion-types";

// WF-ADM-03 — specs/modules/administration/wireframes.md
type TipoIdentidad = "USUARIO" | "PERSONAL";

export default function PaginaIdentidades() {
  const router = useRouter();
  const [tipo, setTipo] = useState<TipoIdentidad>("USUARIO");
  const [nombre, setNombre] = useState("");
  const [documento, setDocumento] = useState("");
  const [correo, setCorreo] = useState("");
  const [telefono, setTelefono] = useState("");
  const [institucion, setInstitucion] = useState("");
  const [dependencia, setDependencia] = useState("");
  const [idCargo, setIdCargo] = useState("");
  const [cargos, setCargos] = useState<Cargo[]>([]);
  const [unidades, setUnidades] = useState<Unidad[]>([]);
  const [ocupada, setOcupada] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [tono, setTono] = useState<"muted" | "error" | "exito">("muted");
  const [correoGuardado, setCorreoGuardado] = useState<string | null>(null);

  useEffect(() => {
    let cancelado = false;
    Promise.all([listarCargos(), listarUnidades()])
      .then(([c, u]) => {
        if (!cancelado) {
          setCargos(c.datos);
          setUnidades(u.datos);
        }
      })
      .catch((err) => {
        if (cancelado) return;
        if (err instanceof ApiRequestError && err.status === 401) {
          router.replace("/login?motivo=sesion_vencida");
        }
      });
    return () => {
      cancelado = true;
    };
  }, [router]);

  async function guardar(evento: FormEvent) {
    evento.preventDefault();
    setOcupada(true);
    setMensaje(null);
    setCorreoGuardado(null);
    try {
      if (tipo === "USUARIO") {
        await crearUsuarioIdentidad({ nombre, documento, correo, telefono, institucion, dependencia });
      } else {
        await crearFichaPersonal({
          nombre, documento, correo, telefono, id_cargo: Number(idCargo),
        });
      }
      setCorreoGuardado(correo);
      setMensaje(tipo === "USUARIO" ? "Identidad guardada." : "Ficha guardada.");
      setTono("exito");
    } catch (error) {
      setMensaje(mensajeError(error));
      setTono("error");
    } finally {
      setOcupada(false);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">Identidades</h1>
      <div className="flex gap-4 text-sm text-text" role="radiogroup" aria-label="Tipo de identidad">
        {(["USUARIO", "PERSONAL"] as const).map((t) => (
          <label key={t} className="flex items-center gap-1">
            <input type="radio" name="tipo" checked={tipo === t} onChange={() => setTipo(t)} />
            {t === "USUARIO" ? "Usuario" : "Personal"}
          </label>
        ))}
      </div>
      <form onSubmit={(e) => void guardar(e)} className="flex flex-col gap-4">
        <Field id="ident-nombre" label="Nombre" value={nombre}
          onChange={(e) => setNombre(e.target.value)} required />
        <Field id="ident-documento" label="Documento" value={documento}
          onChange={(e) => setDocumento(e.target.value)} required />
        <Field id="ident-correo" label="Correo" type="email" value={correo}
          onChange={(e) => setCorreo(e.target.value)} required />
        <Field id="ident-telefono" label="Teléfono" value={telefono}
          onChange={(e) => setTelefono(e.target.value)} required />
        {tipo === "USUARIO" ? (
          <>
            <Field id="ident-institucion" label="Institución" value={institucion}
              onChange={(e) => setInstitucion(e.target.value)} required />
            <Field id="ident-dependencia" label="Dependencia" value={dependencia}
              onChange={(e) => setDependencia(e.target.value)} required />
          </>
        ) : (
          <Select id="ident-cargo" label="Cargo" value={idCargo}
            onChange={(e) => setIdCargo(e.target.value)} required>
            <option value="">Seleccionar</option>
            {cargos.map((c) => (
              <option key={c.id_cargo} value={c.id_cargo}>
                {c.nombre_cargo} ({unidades.find((u) => u.id_unidad === c.id_unidad)?.nombre ?? `unidad ${c.id_unidad}`})
              </option>
            ))}
          </Select>
        )}
        <RegionMensaje texto={ocupada ? "Guardando…" : mensaje} tono={ocupada ? "muted" : tono} />
        <div>
          <Button type="submit" variant="primary" loading={ocupada}>Guardar</Button>
        </div>
      </form>
      {correoGuardado && (
        <p className="text-sm text-text">
          Para invitar su cuenta, continúe en{" "}
          <Link
            href={`/administracion/cuentas/invitar?correo=${encodeURIComponent(correoGuardado)}${tipo === "PERSONAL" ? "&tipo=PERSONAL" : ""}`}
            className="font-bold text-primary-2"
          >
            Invitar una cuenta
          </Link>
          .
        </p>
      )}
    </div>
  );
}

function mensajeError(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.error.codigo === "CONFLICTO") return "Esos datos ya están registrados en otra identidad.";
    if (error.error.codigo === "VALIDACION") return "Revisa los datos ingresados.";
    if (error.status === 429) return "La operación está temporalmente limitada.";
  }
  return "No se pudo guardar.";
}
