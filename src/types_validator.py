from typing import Set, Callable
from src.models import UserRecord, TypeValidationError


class AFD:
    """
    Representação formal de um Autômato Finito Determinístico (Sipser, Cap. 1).
    M = (Q, Sigma, delta, q0, F)
    """
    def __init__(
        self,
        estados: Set[str],
        pertence_alfabeto: Callable[[str], bool],
        delta: Callable[[str, str], str],
        estado_inicial: str,
        estados_finais: Set[str]
    ) -> None:
        self.estados = estados
        self.pertence_alfabeto = pertence_alfabeto
        self.delta = delta
        self.q0 = estado_inicial
        self.F = estados_finais

    def reconhece(self, cadeia: str) -> bool:
        if not cadeia:
            return False

        estado_atual = self.q0
        for simbolo in cadeia:
            if not self.pertence_alfabeto(simbolo):
                return False
            estado_atual = self.delta(estado_atual, simbolo)
            if estado_atual == "q_erro":
                return False

        return estado_atual in self.F


# --- AFD para Inteiros (id e idade) ---
# Sigma = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
# Q = {q0, q1, q_erro}, F = {q1}
def delta_inteiro(estado: str, simbolo: str) -> str:
    if estado == "q0" and simbolo.isdigit():
        return "q1"
    elif estado == "q1" and simbolo.isdigit():
        return "q1"
    return "q_erro"

afd_inteiro = AFD(
    estados={"q0", "q1", "q_erro"},
    pertence_alfabeto=lambda c: c.isdigit(),
    delta=delta_inteiro,
    estado_inicial="q0",
    estados_finais={"q1"}
)


# --- AFD para Texto (nome) ---
# Sigma = caracteres alfabéticos (incluindo acentuados latinos) e espaços
# Q = {q0, q1, q_erro}, F = {q1}
def eh_caractere_alfabetico(c: str) -> bool:
    return c.isalpha() or c.isspace()

def delta_texto(estado: str, simbolo: str) -> str:
    if estado == "q0":
        if simbolo.isalpha():
            return "q1"
        return "q_erro"
    elif estado == "q1":
        if simbolo.isalpha() or simbolo.isspace():
            return "q1"
        return "q_erro"
    return "q_erro"

afd_texto = AFD(
    estados={"q0", "q1", "q_erro"},
    pertence_alfabeto=eh_caractere_alfabetico,
    delta=delta_texto,
    estado_inicial="q0",
    estados_finais={"q1"}
)


def validate_user_types(user: UserRecord) -> bool:
    """
    Valida os campos de um UserRecord usando os AFDs correspondentes.
    Lança TypeValidationError caso algum campo não obedeça às restrições.
    """
    id_val = user.id_token.value.strip()
    nome_val = user.name_token.value.strip()
    idade_val = user.age_token.value.strip()

    if not afd_inteiro.reconhece(id_val):
        raise TypeValidationError(line=user.line, raw_line=user.raw_line)

    if not afd_texto.reconhece(nome_val):
        raise TypeValidationError(line=user.line, raw_line=user.raw_line)

    if not afd_inteiro.reconhece(idade_val):
        raise TypeValidationError(line=user.line, raw_line=user.raw_line)

    return True
